from cgps import *
import time

def NewPosition(Position):
	print("Callback: ", Position)

def LockChanged(GotLock):
	print("Lock " + ("GAINED" if GotLock else "LOST"))

print("Creating GPS object ...")
mygps = GPS(when_new_position=NewPosition, when_lock_changed=LockChanged)
	
print("loop ...")
while 1:
	time.sleep(1)
	position = mygps.position()
	print ("Posn: ", position.time, position.lat, position.lon, position.alt, position.fix)

