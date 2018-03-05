# Python Tracker Module - tracker.py

This library uses the other modules (GPS, RTTY etc.) to build a complete tracker.

## Sample Usage (from pytrack.py)

	```
	from pytrack.tracker import *
	from time import sleep

	mytracker = Tracker()

	mytracker.set_rtty(payload_id='PIP1', frequency=434.100, baud_rate=300, image_packet_ratio=4)
	mytracker.add_rtty_camera_schedule('images/RTTY', period=60, width=320, height=240)

	mytracker.set_lora(payload_id='PIP2', channel=0, frequency=434.150, mode=1, image_packet_ratio=6)
	mytracker.add_lora_camera_schedule('images/LORA', period=60, width=640, height=480)

	mytracker.add_full_camera_schedule('images/FULL', period=60, width=0, height=0)

	mytracker.start()

	while True:
		sleep(1)
```

## Reference

### Object Creation

	`Tracker()`

### Functions

	`set_rtty(payload_id='PIP1', frequency=434.100, baud_rate=300, image_packet_ratio=4)`

This sets the RTTY payload ID, radio frequency, baud rate (use 50 for telemetry only, 300 (faster) if you want to include image data), and ratio of image packets to telemetry packets.

If you don't want RTTY transmissions, just don't call this function.

Note that the RTTY stream will only include image packets if you add a camera schedule (see add_rtty_camera_schedule)

	set_lora(payload_id='PIP2', channel=0, frequency=434.150, mode=1, image_packet_ratio=6)

This sets the LoRa payload ID, radio frequency, mode (use 0 for telemetry-only; 1 (which is faster) if you want to include images), and ratio of image packets to telemetry packets.

If you don't want RTTY transmissions, just don't call this function.

Note that the RTTY stream will only include image packets if you add a camera schedule (see add_rtty_camera_schedule)


	add_rtty_camera_schedule('images/RTTY', period=60, width=320, height=240)

Adds an RTTY camera schedule.  For this example, an image of size 320x240 pixels will be taken every 60 seconds and the resulting file saved in the images/RTTY folder.

Similar functions exist for the LoRa channel and for full-sized images:

	add_lora_camera_schedule('images/LORA', period=60, width=640, height=480)

	add_full_camera_schedule('images/FULL', period=60, width=0, height=0)

Note that specifying width and height of zero results in the camera taking full-sized images (exact resolution depends on the camera model), and that this is the default if those parameters are not included in the call.

	start()

Starts the tracker.  Specifically, it:

1. Loads the LED module to control the LEDs according to GPS status
2. Loads the temperature module to periodically measure temperature on the PITS board
3. Loads the GPS module to get GPS positions
4. Loads the camera module (if at least one camera schedule was added) to follow those schedules
5. Creates a thread to send telemetry and camera image packets to RTTY and/or LoRa radios

	set_sentence_callback(extra_telemetry)

This specifies a function to be called whenever a telemetry sentence is built.  That function should return a string containing a comma-separated list of fields to append to the telemetry sentence.  e.g.:

	def extra_telemetry():
	    extra_value1 = 123.4
	    extra_value2 = 42
	    return "{:.1f}".format(extra_value1) + ',' + "{:.0f}".format(extra_value2)

There is also a callback for images:

	set_image_callback(take_photo)

The callback function is called whenever an image is required.  **If you specify this callback, then it's up to you to provide code to take the photograph**.  Here's an example:

	def take_photo(filename, width, height, gps):
		with picamera.PiCamera() as camera:
			camera.resolution = (width, height)
			camera.start_preview()
			time.sleep(2)
			camera.capture(filename)
			camera.stop_preview()

Use the gps object if you want to add a telemetry overlay, or use different image sizes at different altitudes, for example.
