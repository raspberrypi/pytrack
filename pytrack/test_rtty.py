from pytrack.rtty import *
from time import sleep

global SentOK
SentOK = False

print("Create RTTY object")
rtty = RTTY()

print("Send RTTY Sentence")
rtty.send_text("$$PYSKY,1,10:42:56,51.95023,-2.54445,145,8,21.6*EB9C\n")

while rtty.is_sending():
	sleep(0.1)
print("FINISHED")
