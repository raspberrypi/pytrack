from gps import *
import time

print("Creating GPS object ...")
mygps = GPS();

print("Open GPS ...")
mygps.open()
print("GPS open OK")

# mygps.GetPositions()
mygps.run()

while 1:
	sleep(1)
	# print (time.time(), mygps.Position())
