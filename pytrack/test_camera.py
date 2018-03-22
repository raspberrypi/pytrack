from pytrack import SSDVCamera
from time import sleep

camera = SSDVCamera()
camera.take_photos()

while True:
	sleep(1)
print("FINISHED")
