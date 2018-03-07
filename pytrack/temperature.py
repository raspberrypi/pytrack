import os
import time
import threading

class Temperature(object):
	"""
	Reads temperature
	"""
	
	def __init__(self):
		"""Gets the current board temperature from a DS18B20 device on the PITS board """
		self.Temperatures = [0]
		pass
	
	def _get_temperatures(self):
		"""Returns current temperature"""
		Folder = "/sys/bus/w1/devices"
		Folders = os.listdir(Folder)

		for Item in Folders:
			if len(Item) > 3:
				if (Item[0] != 'w') and (Item[2] == '-'):
					Filename = Folder + '/' + Item + '/w1_slave'
					with open(Filename) as f:
						content = f.readlines()			
					# Second line has temperature
					self.Temperatures[0] = int(content[1].split('=')[1]) / 1000.0

	def __temperature_thread(self):
		while True:
			self._get_temperatures()
			time.sleep(10)

					
	def run(self):
		"""
		Uses a thread to read the current DS18B20 temperature every few seconds, available as Temperatures[0]
		
		Worth changing at some point to handle an extra DS18B20, so users can measure external temperature
		"""
		t = threading.Thread(target=self.__temperature_thread)
		t.daemon = True
		t.start()
