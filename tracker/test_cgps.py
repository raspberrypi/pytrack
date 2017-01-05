from cgps import *
import time

print("Creating GPS object ...")
mygps = GPS();

print("run ...")
mygps.run()

print("loop ...")
while 1:
	time.sleep(1)
	print (mygps.Position())
