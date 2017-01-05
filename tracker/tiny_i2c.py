from gpiozero import OutputDevice, InputDevice
from time import sleep
import time

UBLOX = 66
SDA = 27
SCL = 22
DELAY = 0
TIMEOUT = 100

sda = None
scl = None

def BusIsFree():
	return not sda.is_active and not scl.is_active

def I2CDataLow():
	global sda
	
	sda.close()
	sda = OutputDevice(SDA, False, True)

def I2CDataHigh():
	global sda
	
	sda.close()
	sda = InputDevice(SDA, True)
	
def I2CClockLow():
	global scl
	
	scl.close()
	scl = OutputDevice(SCL, False, True)

def I2CClockHigh():
	global scl
	
	scl.close()
	scl = InputDevice(SCL, True)
	
	to = TIMEOUT
	while (to > 0) and (scl.is_active):
		to -= 1
		sleep(0.00001)
	
	
def I2CStart():
	#	Start condition
	#	This is when sda is pulled low when clock is high. This also puls the clock
	#	low ready to send or receive data so both sda and scl end up low after this.

	# bus must be free for start condition
	to = TIMEOUT
	# while (to > 0) and (not BusIsFree()):
		# to -= 1
		# sleep(0.00001)

	# if not BusIsFree():
		# fprintf(stderr, "gps_info: Cannot set start condition\n");
		# bb->Failed = 1;
		# return;

	# start condition is when data line goes low when clock is high
	I2CDataLow()
	I2CClockLow()

def I2CStop():
	# stop condition
	# when the clock is high, sda goes from low to high
	
	I2CDataLow()

	I2CClockHigh()					# clock will be low from read/write, put high

	I2CDataHigh()
	

def I2CSend(value):
	global sda
	
	mask = 0x80

	# clock is already low from start condition
	
	for j in range(8):
		if (value & mask):
			I2CDataHigh()
		else:
			I2CDataLow()
		
		# clock out data
		I2CClockHigh()
		I2CClockLow()
		mask >>= 1

	# release bus for slave ack or nack
	I2CDataHigh()
	I2CClockHigh() 					# clock high tels slave to NACK/ACK
	rv = not sda.is_active			# get ACK, NACK from slave

	I2CClockLow()

	return rv

def I2CRead(ack):
	global sda
	
	# receive 1 char from bus
	# send: 1=nack, (last byte) 0 = ack (get another)
    
	data = 0

	for j in range(8):
		data <<= 1					# shift in
		I2CClockHigh()				# set clock high to get data
		
		if not sda.is_active:
			data += 1;				# get data
		
		I2CClockLow()

	# clock has been left low at this point
	# send ack or nack
   
	if ack:
		I2CDataHigh()
	else:
		I2CDataLow()
   
	I2CClockHigh()					# clock it in
	I2CClockLow()
	I2CDataHigh()

	return data

	
def GPSGetc():
	# read one byte from GPS

	I2CStart()
	I2CSend(UBLOX * 2 + 1)		# address
	Character = I2CRead(1)
	I2CStop()
		
	return Character


def I2COpen():
	global sda, scl
	sda = InputDevice(SDA, True)
	scl = InputDevice(SCL, True)

I2COpen()

TimeStart = time.clock()

while True:
	Character = GPSGetc()
	if chr(Character) == '$':
		TimeStart = time.clock()
		
	if Character == 255:
		# sleep(0.01)
		print(".", end="")
	else:
		print(chr(Character), end="")
		if Character == 10:
			print("")
			print(time.clock() - TimeStart)

print("Done")
