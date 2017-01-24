from cgps import *
import time

def NewPosition(Position):
	print("Callback: ", Position)

def LockChanged(GotLock):
	print("Lock " + ("GAINED" if GotLock else "LOST"))

print("Creating GPS object ...")
mygps = GPS(WhenNewPosition=NewPosition, WhenLockChanged=LockChanged)
	
print("loop ...")
while 1:
	time.sleep(1)
	# print ("Position: ", mygps.Position())

