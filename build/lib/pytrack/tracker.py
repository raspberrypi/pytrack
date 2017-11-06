from cgps import *
from led import *
from rtty import *
from lora import *
from camera import *
from telemetry import *
from temperature import *
from camera import SSDVCamera
import threading
import configparser

class Tracker(object):
	# HAB Radio/GPS Tracker
	
	def __init__(self):
		self.camera = None
		self.lora = None
		self.rtty = None
		self.SentenceCallback = None
		self.ImageCallback = None		
	
	def _TransmitIfFree(self, Channel, PayloadID, ChannelName, ImagePacketsPerSentence):
		if not Channel.is_sending():
			# Do we need to send an image packet or sentence ?
			# print("ImagePacketCount = ", Channel.ImagePacketCount, ImagePacketsPerSentence)
			if (Channel.ImagePacketCount < ImagePacketsPerSentence) and self.camera:
				Packet = self.camera.get_next_ssdv_packet(ChannelName)
			else:
				Packet = None
				
			if Packet == None:
				print("Sending telemetry sentence for " + PayloadID)

				Channel.ImagePacketCount = 0
				
				# Get temperature
				InternalTemperature = self.temperature.Temperatures[0]
				
				# Get GPS position
				position = self.gps.position()

				# Build sentence
				Channel.SentenceCount += 1

				fieldlist = [PayloadID,
						     Channel.SentenceCount,
						     position.time,
						     "{:.5f}".format(position.lat),
						     "{:.5f}".format(position.lon),
						     int(position.alt),
						     position.sats,
						     "{:.1f}".format(InternalTemperature)]
							 
				if self.SentenceCallback:
					fieldlist.append(self.SentenceCallback())

				sentence = build_sentence(fieldlist)
				print(sentence, end="")
						
				# Send sentence
				Channel.send_text(sentence)
			else:
				Channel.ImagePacketCount += 1
				print("Sending SSDV packet for " + PayloadID)
				Channel.send_packet(Packet[1:])
			
	def set_rtty(self, payload_id='CHANGEME', frequency=434.200, baud_rate=50, image_packet_ratio=4):
		self.RTTYPayloadID = payload_id
		self.RTTYFrequency = frequency
		self.RTTYBaudRate = baud_rate
		self.RTTYImagePacketsPerSentence = image_packet_ratio

		self.rtty = RTTY(self.RTTYFrequency, self.RTTYBaudRate)
		
	def set_lora(self, payload_id='CHANGEME', channel=0, frequency=424.250, mode=1, camera=False, image_packet_ratio=6):
		self.LoRaPayloadID = payload_id
		self.LoRaChannel = channel
		self.LoRaFrequency = frequency
		self.LoRaMode = mode
		self.LORAImagePacketsPerSentence = image_packet_ratio
		
		self.lora = LoRa(self.LoRaChannel, self.LoRaFrequency, self.LoRaMode)
	
	def add_rtty_camera_schedule(self, path='images/RTTY', period=60, width=320, height=240):
		if not self.camera:
			self.camera = SSDVCamera()
		if self.RTTYBaudRate >= 300:
			print("Enable camera for RTTY")
			self.camera.add_schedule('RTTY', self.RTTYPayloadID, path, period, width, height)
		else:
			print("RTTY camera schedule not added - baud rate too low (300 minimum needed")
	
	def add_lora_camera_schedule(self, path='images/LORA', period=60, width=640, height=480):
		if not self.camera:
			self.camera = SSDVCamera()
		if self.LoRaMode == 1:
			print("Enable camera for LoRa")
			self.camera.add_schedule('LoRa0', self.LoRaPayloadID, path, period, width, height)
		else:
			print("LoRa camera schedule not added - LoRa mode needs to be set to 1 not 0")
		
	def add_full_camera_schedule(self, path='images/FULL', period=60, width=0, height=0):
		# 0,0 means "use full camera resolution"
		if not self.camera:
			self.camera = SSDVCamera()
		self.camera.add_schedule('FULL', '', path, period, width, height)
	
	def set_sentence_callback(self, callback):
		self.SentenceCallback = callback
		
	def set_image_callback(self, callback):
		self.ImageCallback = callback
		
	def __ImageCallback(self, filename, width, height):
		self.ImageCallback(filename, width, height, self.gps)
	
	def __transmit_thread(self):
		while True:
			if self.rtty:
				self._TransmitIfFree(self.rtty, self.RTTYPayloadID, 'RTTY', self.RTTYImagePacketsPerSentence)
			if self.lora:
				self._TransmitIfFree(self.lora, self.LoRaPayloadID, 'LoRa0', self.LORAImagePacketsPerSentence)
			sleep(0.01)
			
	def start(self):	
		LEDs = PITS_LED()
		
		self.temperature = Temperature()
		self.temperature.run()
			
		self.gps = GPS(when_lock_changed=LEDs.gps_lock_status)
		
		if self.camera:
			if self.ImageCallback:
				self.camera.take_photos(self.__ImageCallback)
			else:
				self.camera.take_photos(None)
			
		t = threading.Thread(target=self.__transmit_thread)
		t.daemon = True
		t.start()
