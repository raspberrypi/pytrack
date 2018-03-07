import crcmod

def crc16_ccitt(data):
	"""Returns 16-bit CCITT CRC as used by UKHAS"""
	crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')
	return hex(crc16(data))[2:].upper().zfill(4)

def build_sentence(values):
	"""
	Builds a UKHAS sentence from a list of fields.

	values is a list containing all fields to be combined into a sentence.  At a minimum this should have, at the start of the list and in this sequence, the following:

	1. Payload ID (unique to this payload, and different between RTTY and LoRa)
	2. Count (a counter from 1 upwards)
	3. Time (current UTC (GMT) time)
	4. Latitude (latitude in decimal degrees)
	5. Longitude (longitude in decimal degrees)
	6. Altitude (altitude in metres)

	Subsequent fields are optional.

	The resulting sentence will be of this form:

	$$payload_id,count,time,latitude,longitude,altitude*CRC\n

	where CRC is the CRC16_CCITT code for all characters in the string after the $$ and before the *, and "\n" is linefeed.	
	"""
	temp = ','.join(map(str, values))
	sentence = '$$' + temp + '*' + crc16_ccitt(temp.encode()) + '\n'
	return sentence
	