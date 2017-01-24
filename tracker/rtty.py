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
		self.SentenceCount = 0
		self.ImagePacketCount = 0
		self.sending = False
		self.CallbackWhenSent = None
		
		self._set_frequency(frequency)
		
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
		self.send_packet(sentence.encode(), callback)
