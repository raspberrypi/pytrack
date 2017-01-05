from gpiozero import LED
from time import sleep

class PITS_LED(object):
	""" Provides control over the OK and Warn LEDs on the PITS+ / PITS Zero boards
	These LEDs are on BCM pins 26 (OK) and 19 (Warn) for the above boards
	Earlier boards (for the model A/B) had different allocations but are not currently supported
	
	To use, just create a PITS_LED object, then call one of the following functions to show
	the current tracker status:
	
	fail() - shows that software cannot operate normally (e.g. misconfigured).  OK/Warn flashing
	GPS_NoLock() - waiting on a GPS lock.  OK off; Warn flashing
	GPS_OK() - 3D gps lock achieved.  OK flashing; Warn off
	power_save() - Save power as we're flying.  OK and Warn both off.
	"""
	
	def __init__(self):
		self.LED_OK = LED(26)
		self.LED_Warn = LED(19)
	
	def fail(self):
		""" shows that software cannot operate normally (e.g. misconfigured).  OK/Warn flashing """
		self.LED_OK.blink(0.2,0.2)
		sleep(0.2)
		self.LED_Warn.blink(0.2,0.2)
		
	def GPS_NoLock(self):
		""" waiting on a GPS lock.  OK off; Warn flashing """
		self.LED_OK.off()
		self.LED_Warn.blink(0.5,0.5)
	
	def GPS_OK(self):
		""" 3D gps lock achieved.  OK flashing; Warn off """
		self.LED_OK.blink(0.5,0.5)
		self.LED_Warn.off()
		
	#power_save() - Save power as we're flying.  OK and Warn both off.
	