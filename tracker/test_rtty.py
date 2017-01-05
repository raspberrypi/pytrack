from rtty import *
from time import sleep

global SentOK
SentOK = False

# def rtty_done():
	# global SentOK
	# print("CALLBACK")
	# SentOK = True
	

rtty = RTTY()

# SentOK = False
# rtty.send_text("$$PYSKY,1,10:42:56,51.95023,-2.54445,145,8,21.6*EB9C\n", rtty_done)
#while not SentOK:

rtty.send_text("$$PYSKY,1,10:42:56,51.95023,-2.54445,145,8,21.6*EB9C\n")
while rtty.is_sending():
	sleep(0.1)
print("FINISHED")
