from lora import *
import time

mylora = LoRa(0, 434.444, 1)

#mylora.SetLoRaFrequency(434.444)

#mylora.SetStandardLoRaParameters(1)

mylora.send_text("$$Hello World\n")

while mylora.is_sending():
	time.sleep(0.01)

