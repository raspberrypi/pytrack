from tracker import *

mytracker = Tracker();

if mytracker.open(rtty_payload_id='PYSKY', rtty_frequency=434.250, rtty_baud_rate=50, lora_channel=0, lora_payload_id='PYSKY2', lora_frequency=434.450, lora_mode=1, enable_camera=True):
	mytracker.run()
else:
	print("Tracker failed to open")

