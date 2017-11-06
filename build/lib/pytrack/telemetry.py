import crcmod

def crc16_ccitt(data):
    crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')
    return hex(crc16(data))[2:].upper().zfill(4)

def build_sentence(values):
	temp = ','.join(map(str, values))
	sentence = '$$' + temp + '*' + crc16_ccitt(temp.encode()) + '\n'
	return sentence
	