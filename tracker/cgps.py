import math
import socket
import json
import threading

class GPS(object):
	"""
	Gets position from UBlox GPS receiver, using external program for s/w i2c to GPIO pins
	Provides callbacks on change of state (e.g. lock attained, lock lost)
	"""
	PortOpen = False
	
	def __init__(self):
		self._WhenLockGained = None
		self._WhenLockLost = None
		self.GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0, 'fixt': 0}
		
	def open(self):
		return True
	
	def __process_gps(self, s):
		while 1:
			reply = s.recv(4096)                                     
			if reply:
				inputstring = reply.split(b'\n')
				for line in inputstring:
					if line:
						temp = line.decode('utf-8')
						j = json.loads(temp)
						self.GPSPosition = j
			else:
				time.sleep(1)
			
		s.close()
		
	def __doGPS(self, host, port):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

			s.connect((host, port))                               
			
			self.__process_gps(s)

			s.close()
		except:
			pass
		
	def __gps_thread(self):
		host = '127.0.0.1'
		port = 6005
		
		while 1:
			self.__doGPS(host, port)

					
	def Position(self):
		return self.GPSPosition
			
	@property
	def WhenLockGained(self):
		return self._WhenLockGained

	@WhenLockGained.setter
	def WhenLockGained(self, value):
		self._WhenLockGained = value
	
	@property
	def WhenLockLost(self):
		return self._WhenLockLost

	@WhenLockLost.setter
	def WhenLockGained(self, value):
		self._WhenLockLost = value
	
	def run(self):
		t = threading.Thread(target=self.__gps_thread)
		t.daemon = True
		t.start()
