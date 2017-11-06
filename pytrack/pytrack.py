from tracker import *
from time import sleep

def extra_telemetry():
	# sample code to add one telemetry field
    extra_value = 123.4
    return "{:.1f}".format(extra_value)

def take_photo(filename, width, height, gps):
	# sample code to take a photo
	# Use the gps object if you want to add a telemetry overlay, or use different image sizes at different altitudes, for example
	with picamera.PiCamera() as camera:
		camera.resolution = (width, height)
		camera.start_preview()
		time.sleep(2)
		camera.capture(filename)
		camera.stop_preview()					

mytracker = Tracker()

mytracker.set_rtty(payload_id='PIP1', frequency=434.100, baud_rate=300, image_packet_ratio=4)
mytracker.add_rtty_camera_schedule('images/RTTY', period=60, width=320, height=240)

mytracker.set_lora(payload_id='PIP2', channel=0, frequency=434.150, mode=1, image_packet_ratio=6)
mytracker.add_lora_camera_schedule('images/LORA', period=60, width=640, height=480)

mytracker.add_full_camera_schedule('images/FULL', period=60, width=1024, height=768)

# mytracker.set_sentence_callback(extra_telemetry)

# mytracker.set_image_callback(take_photo)

mytracker.start()

while True:
	sleep(1)
