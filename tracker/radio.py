class Radio(object):
	# Radio - RTTY, LoRa
	Emulation = False
	ChannelOpen = False
	
	def __init__(self):
		pass
	
	def open(self):
		# Open connection to radio device
		# Return True if connected OK, False if not
		ChannelOpen = True
		
		return ChannelOpen
	
	def build_sentence(self, values):
		print ("values = ", values)
		return "nothing"