import math
import socket
import json
import threading
import psutil
from os import system
from time import sleep

class GPS(object):
	"""
	Gets position from UBlox GPS receiver, using external program for s/w i2c to GPIO pins
	Provides callbacks on change of state (e.g. lock attained, lock lost)
	"""
	PortOpen = False
	
	def __init__(self, WhenNewPosition=None, WhenLockChanged=None):
		self._WhenLockChanged = WhenLockChanged
		self._WhenNewPosition = WhenNewPosition
		self._GotLock = False
		self._GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0, 'fix': 0}
		
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
						GotLock = self._GPSPosition['fix'] >= 2
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
		system("sudo ../gps/gps > /dev/null &")
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

					
	def Position(self):
		return self._GPSPosition
			
