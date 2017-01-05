from cgps import *
from led import *
from rtty import *
from lora import *
from camera import *
from telemetry import *
from temperature import *
from camera import SSDVCamera

class Tracker(object):
	# HAB Radio/GPS Tracker
	Emulation = False
	
	TrackerOpen = False
	def __init__(self):
		pass
	
	def open(self, RTTYPayloadID, RTTYFrequency, RTTYBaudRate, LoRaPayloadID, LoRaFrequency, LoRaMode, EnableCamera=True):
		# Open connections to GPS, radio etc
		# Return True if connected OK, False if not
		
		TrackerOpen = False
		
		LEDs = PITS_LED()
		LEDs.GPS_NoLock()
		
		self.temperature = Temperature()

		if EnableCamera:
			self.camera = SSDVCamera()
		else:
			self.camera = None
		
		self.gps = GPS()
		
		self.rtty = RTTY(RTTYFrequency, RTTYBaudRate)
		
		self.lora = LoRa(0, LoRaFrequency, LoRaMode)
		
		self.RTTYPayloadID = RTTYPayloadID
		self.LoRaPayloadID = LoRaPayloadID
		
		if self.gps.open():
			TrackerOpen = True
			
			## Connect GPS status to LEDs
			self.gps.WhenLockGained = LEDs.GPS_OK
			
			self.gps.run()	
		else:
			pass
			LEDs.fail()
			
		return TrackerOpen

	def TransmitIfFree(self, Channel, PayloadID, ChannelName):
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
				InternalTemperature = 21	# self.temperature.GetTemperatures()[0]
				
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
			
	
	def run(self):
		if self.camera:
			# self.camera.add_schedule('RTTY', 'PYSKY', 'images/RTTY', 30, 640, 480)
			self.camera.add_schedule('LoRa0', 'PYSKY2', 'images/LoRa0', 30, 640, 480)
			self.camera.take_photos()

		while True:
			self.TransmitIfFree(self.rtty, self.RTTYPayloadID, 'RTTY')
			self.TransmitIfFree(self.lora, self.LoRaPayloadID, 'LoRa0')
			sleep(0.01)
			