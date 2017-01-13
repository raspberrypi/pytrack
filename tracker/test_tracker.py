from tracker import *

mytracker = Tracker();

if mytracker.open(RTTYPayloadID='PYSKY', RTTYFrequency=434.250, RTTYBaudRate=50, LoRaPayloadID='PYSKY2', LoRaFrequency=434.450, LoRaMode=1, EnableCamera=True):
	mytracker.run()
else:
	print("Tracker failed to open")

