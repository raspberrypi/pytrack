from sw_i2c import *
# from pigpio_i2c import *

UBLOX = 66

print("Creating I2C object ...")
i2c = SWI2C();

print("Open I2C ...")
i2c.open()
Line = ''

while True:
	Byte = i2c.getc(UBLOX)
	Character = chr(Byte)

	if Byte == 255:
		sleep(0.1)
	elif Character == '$':
		Line = Character
	elif len(Line) > 90:
		Line = ''
	elif (Line != '') and (Character != '\r'):
		Line = Line + Character
		if Character == '\n':
			print(Line, end="")
			# ProcessLine(Line)
			
			# if (++SentenceCount > 100) SentenceCount = 0;
			
			# if ((SentenceCount == 10) && Config.Power_Saving)
			# {
				# setGPS_GNSS(&bb);
			# }					
			# else if ((SentenceCount == 20) && Config.Power_Saving)
			# {
				# setGPS_DynamicModel6(&bb);
			# }
			# else if (SentenceCount == 30)
			# {
				# SetPowerMode(&bb, Config.Power_Saving && (GPS->Satellites > 4));
			# }
			# else if (SentenceCount == 40)
			# {
				# SetFlightMode(&bb);
			# }

			Line = ''
			sleep(0.1)
		
		
print("Done")

