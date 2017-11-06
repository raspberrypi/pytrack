import os
import time
import threading

class Temperature(object):
	"""
	Reads temperature
	"""
	
	def __init__(self):
		self.Temperatures = [0]
		pass
	
	def _get_temperatures(self):
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
		self._get_temperatures()
		time.sleep(10)

					
	def run(self):
		t = threading.Thread(target=self.__temperature_thread)
		t.daemon = True
		t.start()
