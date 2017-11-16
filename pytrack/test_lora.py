from pytrack.lora import *
import time

print("Create LoRa object")
mylora = LoRa(Channel=0, Frequency=434.450, Mode=1)

print("Send message")
mylora.send_text("$$Hello World\n")

while mylora.is_sending():
	time.sleep(0.01)
print("DONE")
