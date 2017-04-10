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
		self.camera = picamera.PiCamera()
		self.Schedule = []

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
					self.camera.resolution = (item['Width'], item['Height'])				
					filename = item['TargetFolder'] +  time.strftime("%H_%M_%S", time.gmtime()) + '.jpg'
					print("Taking image " + filename)
					self.camera.capture(filename)
					
				# Choose and convert yet?
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
		self.Schedule = []
		
	def add_schedule(self, Channel, Callsign, TargetFolder, Period, Width, Height, VFlip=False, HFlip=False):
		TargetFolder = os.path.join(TargetFolder, '')	

		if not os.path.exists(TargetFolder):
			os.makedirs(TargetFolder)
			
		# Check width/height.  0,0 means use full camera resolution
		if (Width == 0) or (Height == 0):
			try:
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
		print("schedule is: ", self.Schedule)

	def take_photos(self):
		t = threading.Thread(target=self.__photo_thread)
		t.daemon = True
		t.start()
		
	def get_next_ssdv_packet(self, Channel):
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
		

		