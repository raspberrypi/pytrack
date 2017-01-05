import pigpio
from time import sleep
import time

SDA = 27
SCL = 22
DELAY = 0
TIMEOUT = 100


def BusIsFree():
	global gpio
	return gpio.read(SDA) and gpio.read(SCL)

def I2CDataLow():
	global gpio
	gpio.set_mode(SDA, pigpio.OUTPUT) 
	gpio.write(SDA, 0) 

def I2CDataHigh():
	global gpio
	gpio.set_mode(SDA, pigpio.INPUT) 
	gpio.set_pull_up_down(SDA, pigpio.PUD_UP)
	
def I2CClockLow():
	global gpio
	gpio.set_mode(SCL, pigpio.OUTPUT) 
	gpio.write(SCL, 0) 

def I2CClockHigh():
	global gpio
	gpio.set_mode(SCL, pigpio.INPUT)
	gpio.set_pull_up_down(SCL, pigpio.PUD_UP)
	
	to = TIMEOUT
	while (to > 0) and not gpio.read(SCL):
		to -= 1
		sleep(0.00001)


def I2CStart():
	#	Start condition
	#	This is when sda is pulled low when clock is high. This also puls the clock
	#	low ready to send or receive data so both sda and scl end up low after this.

	# bus must be free for start condition
	to = TIMEOUT
	while (to > 0) and (not BusIsFree()):
		to -= 1
		sleep(0.00001)

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
	global gpio

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
	rv = gpio.read(SDA)			# get ACK, NACK from slave

	I2CClockLow()

	return rv

def I2CRead(ack):
	# receive 1 char from bus
	# send: 1=nack, (last byte) 0 = ack (get another)
	global gpio
	
	data = 0

	for j in range(8):
		data <<= 1					# shift in
		I2CClockHigh()				# set clock high to get data
		
		if gpio.read(SDA):
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
	
		
class SWI2C(object):
	"""
	Provides software (bit-banging) I2C implementation
	"""
	
	def __init__(self):
		global gpio
		gpio = pigpio.pi()
	
	def open(self):
		# Open connection to GPS via s/w i2c
		global gpio
		
		# Set SDA and SCL as inputs (these )
		gpio.set_mode(SDA, pigpio.INPUT) 
		gpio.set_mode(SCL, pigpio.INPUT)
		
		gpio.set_pull_up_down(SDA, pigpio.PUD_UP)
		gpio.set_pull_up_down(SCL, pigpio.PUD_UP)
			
	def getc(self, address):
		# read one byte from GPS

		I2CStart()
		I2CSend(address * 2 + 1)
		Character = I2CRead(1)
		I2CStop()
			
		return Character


