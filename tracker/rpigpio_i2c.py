import RPi.GPIO as GPIO
from time import sleep
import time

SDA = 27
SCL = 22
DELAY = 0
TIMEOUT = 100

def BusIsFree():
	return GPIO.input(SDA) and GPIO.input(SCL)

def I2CDataLow():
	GPIO.setup(SDA, GPIO.OUT)
	GPIO.output(SDA, 0)

def I2CDataHigh():
	GPIO.setup(SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
def I2CClockLow():
	GPIO.setup(SCL, GPIO.OUT)
	GPIO.output(SCL, 0)

def I2CClockHigh():
	GPIO.setup(SCL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
	to = TIMEOUT
	while (to > 0) and not GPIO.input(SCL):
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
	rv = GPIO.input(SDA)			# get ACK, NACK from slave

	I2CClockLow()

	return rv

def I2CRead(ack):
	# receive 1 char from bus
	# send: 1=nack, (last byte) 0 = ack (get another)
	
	data = 0

	for j in range(8):
		data <<= 1					# shift in
		I2CClockHigh()				# set clock high to get data
		
		if GPIO.input(SDA):
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
		pass
	
	def open(self):
		# Open connection to GPS via s/w i2c
		
		# Set BCM pin numbering mode
		GPIO.setmode(GPIO.BCM)

		# Set SDA and SCL as inputs (these )
		GPIO.setup(SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(SCL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			
	def getc(self, address):
		# read one byte from GPS

		I2CStart()
		I2CSend(address * 2 + 1)
		Character = I2CRead(1)
		I2CStop()
			
		return Character


