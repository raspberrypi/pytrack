import math
import socket
import json
import threading
import psutil
from os import system
from time import sleep

class GPSPosition(object):
	def __init__(self, when_new_position=None, when_lock_changed=None):
		self.GPSPosition = None
		
	@property
	def time(self):
		return self.GPSPosition['time']

	@property
	def lat(self):
		return self.GPSPosition['lat']
			
	@property
	def lon(self):
		return self.GPSPosition['lon']
			
	@property
	def alt(self):
		return self.GPSPosition['alt']
			
	@property
	def sats(self):
		return self.GPSPosition['sats']
			
	@property
	def fix(self):
		return self.GPSPosition['fix']
		
class GPS(object):
	"""
	Gets position from UBlox GPS receiver, using external program for s/w i2c to GPIO pins
	Provides callbacks on change of state (e.g. lock attained, lock lost)
	"""
	PortOpen = False
	
	def __init__(self, when_new_position=None, when_lock_changed=None):
		self._WhenLockChanged = when_lock_changed
		self._WhenNewPosition = when_new_position
		self._GotLock = False
		self._GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0, 'fix': 0}
		self._GPSPositionObject = GPSPosition()
		
		# Start thread to talk to GPS program
		t = threading.Thread(target=self.__gps_thread)
		t.daemon = True
		t.start()
		
	def __process_gps(self, s):
		while 1:
			reply = s.recv(4096)                                     
			if reply:
				inputstring = reply.split(b'\n')
				for line in inputstring:
					if line:
						temp = line.decode('utf-8')
						j = json.loads(temp)
						self._GPSPosition = j
						if self._WhenNewPosition:
							self._WhenNewPosition(self._GPSPosition)
						GotLock = self._GPSPosition['fix'] >= 1
						if GotLock != self._GotLock:
							self._GotLock = GotLock
							if self._WhenLockChanged:
								self._WhenLockChanged(GotLock)
			else:
				sleep(1)
			
		s.close()
	
	def _ServerRunning(self):
		return "gps" in [psutil.Process(i).name() for i in psutil.pids()]
		
	def _StartServer(self):
		system("pytrack-gps > /dev/null &")
		sleep(1)
		
	def __doGPS(self, host, port):
		try:		
			# Connect socket to GPS server
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
			s.connect((host, port))                               		
			self.__process_gps(s)
			s.close()
		except:
			# Start GPS server if it's not running
			if not self._ServerRunning():
				self._StartServer()
		
	def __gps_thread(self):
		host = '127.0.0.1'
		port = 6005
		
		while 1:
			self.__doGPS(host, port)

					
	def position(self):
		# return self._GPSPosition
		# 		self._GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0, 'fix': 0}
		self._GPSPositionObject.GPSPosition = self._GPSPosition
		return self._GPSPositionObject

		
	@property
	def time(self):
		return self._GPSPosition['time']
			
	@property
	def lat(self):
		return self._GPSPosition['lat']
			
	@property
	def lon(self):
		return self._GPSPosition['lon']
			
	@property
	def alt(self):
		return self._GPSPosition['alt']
			
	@property
	def sats(self):
		return self._GPSPosition['sats']
			
	@property
	def fix(self):
		return self._GPSPosition['fix']
			
