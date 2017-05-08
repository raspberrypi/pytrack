# Python Tracker Module - tracker.py

This library uses the other modules (GPS, RTTY etc.) to build a complete tracker.

## Parameter-based configuration (test_tracker.py)

	from tracker import *
	
	mytracker = Tracker();
	
	if mytracker.open(rtty_payload_id='PYSKY', rtty_frequency=434.250, rtty_baud_rate=50,
						lora_channel=0, lora_payload_id='PYSKY2', lora_frequency=434.450, lora_mode=1,
						enable_camera=True, image_packets_per_sentence=4):
		mytracker.run()
	else:
		print("Tracker failed to open")
	

## File-based configuration (pytrack.py)

	from tracker import *
	
	mytracker = Tracker()
	
	try:
		if mytracker.open(config_filename='pytrack.ini'):
			mytracker.run()
		else:
			print("Tracker failed to open")
	except RuntimeError as e:
		print("Tracker failed to run correctly")
		print(e)

where the INI file is like this (pytrack.ini):

	[RTTY]
	ID = PYSKY
	Frequency = 434.250
	BaudRate = 50
	Camera = 0
	
	[LoRa]
	Channel = 0
	ID = PYSKY2
	Frequency = 434.450
	Mode = 1
	
	[General]
	Camera = 1
	ImagePacketsPerSentence = 4


## Reference

### Object Creation

	Tracker()

### Functions

	open(RTTYPayloadID='CHANGEME', RTTYFrequency=434.100, RTTYBaudRate=300,
			LoRaChannel=0, LoRaPayloadID='CHANGEME2', LoRaFrequency=434.200, LoRaMode=1,
			EnableCamera=True,
			ConfigFileName=None):

This loads and configures the GPS, RTTY and other modules, using the supplied parameters, or the supplied config file.  The supplied parameters are set first, and are used as defaults if ConfigFileName is specified.

- To disable the RTTY channel, set Frequency or Baud Rate to zero or negative
- To disable the LoRa channel, set Frequency to zero or negative, or Mode to negative

	run()

Starts the tracker.  Specifically, it:

1. Adds camera schedules for the RTTY and LoRa channels
2. Adds a camera schedule for full-sized images
3. Runs a loop sending rtty and lora packets as the transmitters become available
4. In the loop, when a channel becomes available, a choice is made of sending a telemetry sentence or SSDV image packet.  1 telemetry sentence is sent for every 4 image packets

Note that for RTTY images, the baud rate needs to be 300; for LoRa images the mode needs to be 1.  If other selections are made then images are disabled for that channel.



