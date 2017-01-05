import os

class Temperature(object):
	"""
	Reads temperature
	"""
	
	def __init__(self):
		pass
	
	def GetTemperatures(self):
		Folder = "/sys/bus/w1/devices"
		Folders = os.listdir(Folder)
		Result = []

		for Item in Folders:
			if len(Item) > 3:
				if (Item[0] != 'w') and (Item[2] == '-'):
					Filename = Folder + '/' + Item + '/w1_slave'
					with open(Filename) as f:
						content = f.readlines()			
					# Second line has temperature
					Result.append(int(content[1].split('=')[1])/1000.0)

		return Result
