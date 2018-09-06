import picamera
import threading
import time
import os
import fnmatch

def SelectBestImage(TargetFolder):
	Result = ''
	Largest = 0
	for item in os.listdir(TargetFolder):
		extension = os.path.splitext(item)[1]
		if extension == '.jpg':
			itemsize = os.path.getsize(TargetFolder + item)
			if itemsize > Largest:
				Result = item
				Largest = itemsize
				
	return Result

def ConvertToSSDV(TargetFolder, FileName, Callsign, ImageNumber, SSDVFileName):
	print('ssdv -e -c ' + Callsign + ' -i ' + str(ImageNumber) + ' ' + TargetFolder + FileName + ' ' + TargetFolder + SSDVFileName)
	os.system('ssdv -e -c ' + Callsign + ' -i ' + str(ImageNumber) + ' ' + TargetFolder + FileName + ' ' + TargetFolder + SSDVFileName)

def MoveFiles(Folder, SubFolder, Extension):
	if not os.path.exists(Folder + SubFolder):
		os.makedirs(Folder + SubFolder)
	for item in os.listdir(Folder):
		if os.path.splitext(item)[1] == Extension:
			os.rename(Folder + item, Folder + SubFolder + '/' + item)
	
class SSDVCamera(object):
	"""
	Simple Pi camera library that uses the picamera library and the SSDV encoder
	"""
	
	def __init__(self):
		# self.camera = picamera.PiCamera()
		self.Schedule = []
		self.ImageCallback = None

	def __find_item_for_channel(self, Channel):
		for item in self.Schedule:
			if item['Channel'] == Channel:
				return item
		return None
	
	def __get_next_ssdv_file(self, item):
		ssdv_filename = item['TargetFolder'] + item['SSDVFileName']
		next_filename = item['TargetFolder'] + item['NextSSDVFileName']
		if os.path.isfile(next_filename):
			if os.path.isfile(ssdv_filename):
				os.remove(ssdv_filename)
			os.rename(next_filename, ssdv_filename)
			return ssdv_filename
			
		return None
		
	def __photo_thread(self):
		while True:
			for item in self.Schedule:
				# Take photo if needed
				if time.monotonic() > item['LastTime']:
					item['LastTime'] = time.monotonic() + item['Period']
					filename = item['TargetFolder'] +  time.strftime("%H_%M_%S", time.gmtime()) + '.jpg'
					if self.ImageCallback:
						self.ImageCallback(filename, item['Width'], item['Height'])
						if not os.path.isfile(filename):
							print("User image callback did not produce the file " + filename)
					else:
						print("Taking image " + filename)
						with picamera.PiCamera() as camera:
							camera.resolution = (item['Width'], item['Height'])				
							camera.start_preview()
							time.sleep(2)
							camera.capture(filename)
							camera.stop_preview()					
						
				# Choose and convert yet?
				if item['Callsign'] != '':
					# Is a radio channel
					if item['PacketIndex'] >= (item['PacketCount'] - 10):
						# SSDV file alread exists ?
						if not os.path.isfile(item['TargetFolder'] + item['NextSSDVFileName']):
							# At least one jpg file waiting for us?
							if len(fnmatch.filter(os.listdir(item['TargetFolder']), '*.jpg')) > 0:
								# Select file to convert
								FileName = SelectBestImage(item['TargetFolder'])
								
								if FileName != None:
									# Convert it
									item['ImageNumber'] += 1
									ConvertToSSDV(item['TargetFolder'], FileName, item['Callsign'], item['ImageNumber'], item['NextSSDVFileName'])

									# Move the jpg files so we don't use them again
									MoveFiles(item['TargetFolder'], time.strftime("%Y_%m_%d", time.gmtime()), '.jpg')
							
			time.sleep(1)

	def clear_schedule(self):
		"""Clears the schedule."""
		self.Schedule = []
		
	def add_schedule(self, Channel, Callsign, TargetFolder, Period, Width, Height, VFlip=False, HFlip=False):
		"""
		Adds a schedule for a specific "channel", and normally you would set a schedule for each radio channel (RTTY and LoRa) and also one for full-sized images that are not transmitted.
		- Channel is a unique name for this entry, and is used to retrieve/convert photographs later
		- Callsign is used for radio channels, and should be the same as used by telemetry on that channel (it is embedded into SSDV packets)
		- TargetFolder is where the JPG files should be saved.  It will be created if necessary.  Each channel should have its own target folder.
		- Period is the time in seconds between photographs.  This should be much less than the time taken to transmit an image, so that there are several images to choose from when transmitting.  Depending on the combination of schedules, and how long each photograph takes, it may not always (or ever) be possible to maintain the specified periods for all channels.
		- Width and Height are self-evident.  Take care not to create photographs that take a long time to send.  If Width or Height are zero then the full camera resolution (as determined by checking the camera model - Omnivision or Sony) is used.
		- VFlip and HFlip can be used to correct images if the camera is not physically oriented correctly. 	
		"""
		TargetFolder = os.path.join(TargetFolder, '')	

		if not os.path.exists(TargetFolder):
			os.makedirs(TargetFolder)
			
		# Check width/height.  0,0 means use full camera resolution
		if (Width == 0) or (Height == 0):
			try:
				with picamera.PiCamera() as camera:
					NewCamera = self.camera.revision == 'imx219'
			except:
				NewCamera = False
			if NewCamera:
				Width = 3280
				Height = 2464
			else:
				Width = 2592
				Height = 1944
				
		
		self.Schedule.append({'Channel': Channel,
							  'Callsign': Callsign,
							  'TargetFolder': TargetFolder,
							  'Period': Period,
							  'Width': Width,
							  'Height': Height,
							  'VFlip': VFlip,
							  'HFlip': HFlip,
							  'LastTime': 0,
							  'ImageNumber': 0,
							  'PacketIndex': 0,
							  'PacketCount': 0,
							  'SSDVFileName': 'ssdv.bin',
							  'NextSSDVFileName': '_ext.bin',
							  'File': None})
		# print("schedule is: ", self.Schedule)

	def take_photos(self, callback=None):
		"""
		Begins execution of the schedule, in a thread.  If the callback is specified, then this is called instead of taking a photo directly.  The callback is called with the following parameters:

		filename - name of image file to create
		width - desired image width in pixels (can be ignored)
		height - desired image height in pixels (can be ignored)

		The callback is expected to take a photograph, using whatever method it likes, and with whatever manipulation it likes, creating the file specified by 'filename'.		
		"""
		self.ImageCallback = callback
		
		t = threading.Thread(target=self.__photo_thread)
		t.daemon = True
		t.start()
		
	def get_next_ssdv_packet(self, Channel):
		"""
		Retrieves the next SSDV packet for a particular channel.
		If there is no image available (i.e. no photograph has been taken and converted yet for this channel) then None is returned.
		Returned packets contain a complete (256-byte) SSDV packet.
		"""
		Result = None
		
		item = self.__find_item_for_channel(Channel)
		if item != None:
			# Open file if we're not reading a file already
			if item['File'] == None:
				# Get next file to read, if there is one
				filename = self.__get_next_ssdv_file(item)
				if filename != None:
					item['PacketIndex'] = 0
					item['PacketCount'] = os.path.getsize(filename) / 256
					item['File'] = open(filename, mode='rb')
					
			# Read from file
			if item['File'] != None:
				Result = item['File'].read(256)
				item['PacketIndex'] += 1
				if item['PacketIndex'] >= item['PacketCount']:
					# Close file if we're at the end
					item['PacketIndex'] = 0
					item['PacketCount'] = 0
					item['File'].close()
					item['File'] = None

		return Result
		

		