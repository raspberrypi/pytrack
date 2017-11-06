from gpiozero import InputDevice
import threading
import spidev
import time

REG_FIFO                   = 0x00
REG_FIFO_ADDR_PTR          = 0x0D 
REG_FIFO_TX_BASE_AD        = 0x0E
REG_FIFO_RX_BASE_AD        = 0x0F
REG_RX_NB_BYTES            = 0x13
REG_OPMODE                 = 0x01
REG_FIFO_RX_CURRENT_ADDR   = 0x10
REG_IRQ_FLAGS              = 0x12
REG_PACKET_SNR				= 0x19
REG_PACKET_RSSI				= 0x1A
REG_CURRENT_RSSI			= 0x1B
REG_DIO_MAPPING_1          = 0x40
REG_DIO_MAPPING_2          = 0x41
REG_MODEM_CONFIG           = 0x1D
REG_MODEM_CONFIG2          = 0x1E
REG_MODEM_CONFIG3          = 0x26
REG_PAYLOAD_LENGTH         = 0x22
REG_IRQ_FLAGS_MASK         = 0x11
REG_HOP_PERIOD             = 0x24
REG_FREQ_ERROR				= 0x28
REG_DETECT_OPT				= 0x31
REG_DETECTION_THRESHOLD	= 0x37

# MODES
RF98_MODE_RX_CONTINUOUS    = 0x85
RF98_MODE_TX               = 0x83
RF98_MODE_SLEEP            = 0x80
RF98_MODE_STANDBY          = 0x81

# Modem Config 1
EXPLICIT_MODE              = 0x00
IMPLICIT_MODE              = 0x01

ERROR_CODING_4_5           = 0x02
ERROR_CODING_4_6           = 0x04
ERROR_CODING_4_7           = 0x06
ERROR_CODING_4_8           = 0x08

BANDWIDTH_7K8              = 0x00
BANDWIDTH_10K4             = 0x10
BANDWIDTH_15K6             = 0x20
BANDWIDTH_20K8             = 0x30
BANDWIDTH_31K25            = 0x40
BANDWIDTH_41K7             = 0x50
BANDWIDTH_62K5             = 0x60
BANDWIDTH_125K             = 0x70
BANDWIDTH_250K             = 0x80
BANDWIDTH_500K             = 0x90

# Modem Config 2

SPREADING_6                = 0x60
SPREADING_7                = 0x70
SPREADING_8                = 0x80
SPREADING_9                = 0x90
SPREADING_10               = 0xA0
SPREADING_11               = 0xB0
SPREADING_12               = 0xC0

CRC_OFF                    = 0x00
CRC_ON                     = 0x04

# POWER AMPLIFIER CONFIG
REG_PA_CONFIG              = 0x09
PA_MAX_BOOST               = 0x8F
PA_LOW_BOOST               = 0x81
PA_MED_BOOST               = 0x8A
PA_MAX_UK                  = 0x88
PA_OFF_BOOST               = 0x00
RFO_MIN                    = 0x00

# LOW NOISE AMPLIFIER
REG_LNA                    = 0x0C
LNA_MAX_GAIN               = 0x23  # 0010 0011
LNA_OFF_GAIN               = 0x00
LNA_LOW_GAIN               = 0xC0  # 1100 0000

class LoRa(object):
	"""
	Radio - LoRa.  Single channel - if you want to use more channels then create more objects.
	"""
	
	def __init__(self, Channel=0, Frequency=434.250, Mode=1, DIO0=0, DIO5=0):
		self.SentenceCount = 0
		self.ImagePacketCount = 0
		self.sending = False
		self.CallbackWhenSent = None
		
		if DIO0 == 0:
			if Channel == 1:
				DIO0 = 16
			else:
				DIO0 = 25

		if DIO5 == 0:
			if Channel == 1:
				DIO5 = 12
			else:
				DIO5 = 24
				
		self.Channel = Channel
		self.Frequency = Frequency
		self.DIO0 = InputDevice(DIO0)
		self.DIO5 = InputDevice(DIO5)
		self.currentMode = 0x81;
		self.Power = PA_MAX_UK
		self.spi = spidev.SpiDev()
		self.spi.open(0, Channel)
		self.spi.max_speed_hz = 976000
		self.__writeRegister(REG_DIO_MAPPING_2, 0x00)
		self.SetLoRaFrequency(Frequency)
		self.SetStandardLoRaParameters(Mode)

	def __readRegister(self, register):
		data = [register & 0x7F, 0]
		result = self.spi.xfer(data)
		return result[1]
		
	def __writeRegister(self, register, value):
		self.spi.xfer([register | 0x80, value])

	def __setMode(self, newMode):
		if newMode != self.currentMode:
			if newMode == RF98_MODE_TX:
				# TURN LNA OFF FOR TRANSMIT
				self.__writeRegister(REG_LNA, LNA_OFF_GAIN)
				
				# Set 10mW
				self.__writeRegister(REG_PA_CONFIG, self.Power)
			elif newMode == RF98_MODE_RX_CONTINUOUS:
				# PA Off
				self.__writeRegister(REG_PA_CONFIG, PA_OFF_BOOST)
				
				# Max LNA Gain
				self.__writeRegister(REG_LNA, LNA_MAX_GAIN)
		
			self.__writeRegister(REG_OPMODE, newMode)
			self.currentMode = newMode
  
			if newMode != RF98_MODE_SLEEP:
				#while not self.DIO5.is_active:
				#	pass
				# time.sleep(0.1)
				pass
		
	def SetLoRaFrequency(self, Frequency):
		self.__setMode(RF98_MODE_STANDBY)
		self.__setMode(RF98_MODE_SLEEP)
		self.__writeRegister(REG_OPMODE, 0x80);
		#self.__setMode(RF98_MODE_SLEEP)
		self.__setMode(RF98_MODE_STANDBY)
		
		FrequencyValue = int((Frequency * 7110656) / 434)
	
		self.__writeRegister(0x06, (FrequencyValue >> 16) & 0xFF)
		self.__writeRegister(0x07, (FrequencyValue >> 8) & 0xFF)
		self.__writeRegister(0x08, FrequencyValue & 0xFF)

	def SetLoRaParameters(self, ImplicitOrExplicit, ErrorCoding, Bandwidth, SpreadingFactor, LowDataRateOptimize):
		self.__writeRegister(REG_MODEM_CONFIG, ImplicitOrExplicit | ErrorCoding | Bandwidth)
		self.__writeRegister(REG_MODEM_CONFIG2, SpreadingFactor | CRC_ON)
		self.__writeRegister(REG_MODEM_CONFIG3, 0x04 | (0x08 if LowDataRateOptimize else 0))
		self.__writeRegister(REG_DETECT_OPT, (self.__readRegister(REG_DETECT_OPT) & 0xF8) | (0x05 if (SpreadingFactor == SPREADING_6) else 0x03))
		self.__writeRegister(REG_DETECTION_THRESHOLD, 0x0C if (SpreadingFactor == SPREADING_6) else 0x0A)
	
		self.PayloadLength = 255 if (ImplicitOrExplicit == IMPLICIT_MODE) else 0
	
		self.__writeRegister(REG_PAYLOAD_LENGTH, self.PayloadLength)
		self.__writeRegister(REG_RX_NB_BYTES, self.PayloadLength)

	def SetStandardLoRaParameters(self, Mode):
		if Mode == 0:
			self.SetLoRaParameters(EXPLICIT_MODE, ERROR_CODING_4_8, BANDWIDTH_20K8, SPREADING_11, True)
		elif Mode == 1:
			self.SetLoRaParameters(IMPLICIT_MODE, ERROR_CODING_4_5, BANDWIDTH_20K8, SPREADING_6, False)
		elif Mode == 2:
			self.SetLoRaParameters(EXPLICIT_MODE, ERROR_CODING_4_8, BANDWIDTH_62K5, SPREADING_8, False)
		
	def _send_thread(self):
		# wait for DIO0
		# while not self.DIO0.is_active:
		while self.DIO5.is_active:
			time.sleep(0.01)
		self.sending = False
		if self.CallbackWhenSent:
			self.CallbackWhenSent()

	def is_sending(self):
		return self.sending
		
	def send_packet(self, packet, callback=None):
		self.CallbackWhenSent = callback
		self.sending = True
		
		self.__setMode(RF98_MODE_STANDBY)
	
		# map DIO0 to TxDone
		self.__writeRegister(REG_DIO_MAPPING_1, 0x40)

		self.__writeRegister(REG_FIFO_TX_BASE_AD, 0x00)
		self.__writeRegister(REG_FIFO_ADDR_PTR, 0x00)

		data = [REG_FIFO | 0x80] + list(packet) + [0]
		self.spi.xfer(data)
		
		self.__writeRegister(REG_PAYLOAD_LENGTH, self.PayloadLength if self.PayloadLength else len(packet))

		self.__setMode(RF98_MODE_TX);

		t = threading.Thread(target=self._send_thread)
		t.daemon = True
		t.start()

	def send_text(self, sentence, callback=None):
		self.send_packet(sentence.encode(), callback)
