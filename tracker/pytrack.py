from tracker import *

mytracker = Tracker()

try:
	if mytracker.open(ConfigFileName='pytrack.ini'):
		mytracker.run()
	else:
		print("Tracker failed to open")
except RuntimeError as e:
	print("Tracker failed to run correctly")
	print(e)
