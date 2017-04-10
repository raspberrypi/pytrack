from cgps import *
from led import *
from rtty import *
from lora import *
from camera import *
from telemetry import *
from temperature import *
from camera import SSDVCamera
import configparser

class Tracker(object):
	# HAB Radio/GPS Tracker
	Emulation = False
	
	TrackerOpen = False
	def __init__(self):
		pass
	
	def _load_settings_file(self, ConfigFileName):
		if ConfigFileName:
			# Open config file
			config = configparser.RawConfigParser()   
			config.read(ConfigFileName)

			self.RTTYPayloadID = config.get('RTTY', 'ID', fallback=self.RTTYPayloadID)
			self.RTTYFrequency = float(config.get('RTTY', 'Frequency', fallback=self.RTTYFrequency))
			self.RTTYBaudRate = int(config.get('RTTY', 'BaudRate', fallback=self.RTTYBaudRate))

			self.LoRaChannel = int(config.get('LoRa', 'Channel', fallback=self.LoRaChannel))
			self.LoRaPayloadID = config.get('LoRa', 'ID', fallback=self.LoRaPayloadID)
			self.LoRaFrequency = float(config.get('LoRa', 'Frequency', fallback=self.LoRaFrequency))
			self.LoRaMode = int(config.get('LoRa', 'Mode', fallback=self.LoRaMode))
			
			self.EnableCamera = config.getboolean('General', 'Camera', fallback=self.EnableCamera)
	
	def _TransmitIfFree(self, Channel, PayloadID, ChannelName):
		if not Channel.is_sending():
			# Do we need to send an image packet or sentence ?
			print("ImagePacketCount = ", Channel.ImagePacketCount)
			if (Channel.ImagePacketCount < 4) and self.camera:
				print("Get SSDV packet")
				Packet = self.camera.get_next_ssdv_packet(ChannelName)
			else:
				Packet = None
				
			if Packet == None:
				print("Get telemetry sentence")

				Channel.ImagePacketCount = 0
				
				# Get temperature
				InternalTemperature = self.temperature.Temperatures[0]
				
				# Get GPS position
				position = self.gps.Position()

				# Build sentence
				Channel.SentenceCount += 1
				sentence = build_sentence([PayloadID,
										   Channel.SentenceCount,
										   position['time'],
										   "{:.5f}".format(position['lat']),
										   "{:.5f}".format(position['lon']),
										   int(position['alt']),
										   position['sats'],
										   "{:.1f}".format(InternalTemperature)])
				print(sentence, end="")
						
				# Send sentence
				Channel.send_text(sentence)
			else:
				Channel.ImagePacketCount += 1
				print("SSDV packet is ", len(Packet), " bytes")
				Channel.send_packet(Packet[1:])
			
	
	def open(self, RTTYPayloadID='CHANGEME', RTTYFrequency=434.100, RTTYBaudRate=300,
					LoRaChannel=0, LoRaPayloadID='CHANGEME2', LoRaFrequency=434.200, LoRaMode=1,
					EnableCamera=True,
					ConfigFileName=None):
		# Open connections to GPS, radio etc
		# Return True if connected OK, False if not
		
		self.RTTYPayloadID = RTTYPayloadID
		self.RTTYFrequency = RTTYFrequency
		self.RTTYBaudRate = RTTYBaudRate
		self.LoRaPayloadID = LoRaPayloadID
		self.LoRaChannel = LoRaChannel
		self.LoRaFrequency = LoRaFrequency
		self.LoRaMode = LoRaMode
		self.EnableCamera = EnableCamera
		
		self._load_settings_file(ConfigFileName)
		
		LEDs = PITS_LED()
		
		self.temperature = Temperature()
		self.temperature.run()
		
		if self.EnableCamera:
			self.camera = SSDVCamera()
		else:
			self.camera = None
		
		self.gps = GPS(WhenLockChanged=LEDs.GPS_LockStatus)
		
		if (self.RTTYFrequency > 0) and (self.RTTYBaudRate):
			self.rtty = RTTY(self.RTTYFrequency, self.RTTYBaudRate)
		else:
			self.rtty = None
		
		if (self.LoRaChannel >= 0) and (self.LoRaFrequency > 0):
			self.lora = LoRa(self.LoRaChannel, self.LoRaFrequency, self.LoRaMode)
		else:
			self.lora = None
			
		return self.rtty and self.lora

	def run(self):
		if self.camera:
			if self.rtty and (self.RTTYBaudRate >= 300):
				print("Enable camera for RTTY")
				self.camera.add_schedule('RTTY', 'PYSKY', 'images/RTTY', 30, 640, 480)
			if self.rtty and (self.LoRaMode == 1):
				print("Enable camera for LoRa")
				self.camera.add_schedule('LoRa0', 'PYSKY2', 'images/LoRa0', 30, 640, 480)
			self.camera.add_schedule('FULL', '', 'images/FULL', 60, 0, 0)		# 0,0 means "use full camera resolution"
			self.camera.take_photos()

		while True:
			if self.rtty:
				self._TransmitIfFree(self.rtty, self.RTTYPayloadID, 'RTTY')
			if self.lora:
				self._TransmitIfFree(self.lora, self.LoRaPayloadID, 'LoRa0')
			sleep(0.01)
			