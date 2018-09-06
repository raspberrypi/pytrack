from gpiozero import OutputDevice
import serial
import threading
import pigpio
import time

class RTTY(object):
	"""
	Radio - RTTY
	"""
	
	def __init__(self, frequency=434.250, baudrate=50):
		"""
		The frequency is in MHz and should be selected carefully:

		- If you are using LoRa also, it should be at least 25kHz (0.025MHz) away from the LoRa frequency
		- It should be different to that used by any other HAB flights that are airborne at the same time and within 400 miles (600km)
		- It should be legal in your country (for the UK see [https://www.ofcom.org.uk/__data/assets/pdf_file/0028/84970/ir_2030-june2014.pdf](https://www.ofcom.org.uk/__data/assets/pdf_file/0028/84970/ir_2030-june2014.pdf "IR2030"))

		The baudrate should be either 50 (best if you are not sending image data over RTTY) or 300 (best if you are).

		When setting up your receiver, use the following settings:

		- 50 or 300 baud
		- 7 data bits (if using 50 baud) or 8 (300 baud)
		- no parity
		- 2 stop bits
		"""
		self.SentenceCount = 0
		self.ImagePacketCount = 0
		self.sending = False
		self.CallbackWhenSent = None
		
		self._set_frequency(frequency)
		self._set_frequency(frequency)	# In case MTX2 wasn't in ready mode when we started
		
		self.ntx2 = OutputDevice(17)
		self.ntx2.off()

		self.ser = serial.Serial()
		self.ser.baudrate = baudrate
		self.ser.stopbits = 2
		if baudrate < 300:
			self.ser.bytesize = 7
		else:
			self.ser.bytesize = 8
		self.ser.port = '/dev/ttyAMA0'
		
	def _set_frequency(self, Frequency):
		pio = pigpio.pi()
		if not pio.connected:
			print()
			print("*** Please start the PIGPIO daemon by typing the following command at the shell prompt:")
			print()
			print("    sudo pigpiod")
			print()
			quit()
			
		_mtx2comp = (Frequency+0.0015)/6.5
		
		_mtx2int = int(_mtx2comp)
		_mtx2fractional = int(((_mtx2comp-_mtx2int)+1) * 524288)
		
		_mtx2command = "@PRG_" + "%0.2X" % (_mtx2int-1) + "%0.6X" % _mtx2fractional + "\r"
		
		pio.set_mode(17, pigpio.OUTPUT)
		
		pio.wave_add_new()
		
		pio.wave_add_serial(17, 9600, _mtx2command, 0, 8, 2)
		
		wave_id = pio.wave_create()

		if wave_id >= 0:
			pio.wave_send_once(wave_id)

			while pio.wave_tx_busy():
				time.sleep(0.1)
		
		pio.stop()

	def _send_thread(self):
		self.ser.close()
		self.sending = False
		if self.CallbackWhenSent:
			self.CallbackWhenSent()

	def is_sending(self):
		return self.sending
		
	def send_packet(self, packet, callback=None):
		"""
		Sends a binary packet packet which should be a bytes object.  Normally this would be a 256-byte SSDV packet (see the camera.py module).

		callback, if used, is called when the packet has been completely set and the RTTY object is ready to accept more data to transmit.		
		"""
		self.CallbackWhenSent = callback
		self.ntx2.on()
		try:
			self.ser.open()
			self.sending = True
			self.ser.write(packet)
			t = threading.Thread(target=self._send_thread)
			t.daemon = True
			t.start()
		except:
			raise RuntimeError('Failed to open RTTY serial port\nCheck that port is present and has been enabled')

	def send_text(self, sentence, callback=None):
		"""
		Sends a text string sentence.  Normally this would be a UKHAS-compatible HAB telemetry sentence but it can be anything.  See the telemetry.py module for how to create compliant telemetry sentences.

		callback is as for send_packet()
		"""
		self.send_packet(sentence.encode(), callback)
