import math
import re
import socket
import json
import threading
import psutil
import serial
from os import system
from time import sleep

class GPSPosition(object):
    def __init__(self, when_new_position=None, when_lock_changed=None):
        self.GPSPosition = None
        
    @property
    def time(self):
        return self.GPSPosition['time']

    @property
    def lat(self):
        return self.GPSPosition['lat']
            
    @property
    def lon(self):
        return self.GPSPosition['lon']
            
    @property
    def alt(self):
        return self.GPSPosition['alt']
            
    @property
    def sats(self):
        return self.GPSPosition['sats']
            
    @property
    def fix(self):
        return self.GPSPosition['fix']
        


class GPS(object):
    def __init__(self,board="pits",when_new_position=None, when_lock_changed=None):
        if board =="pits":
            self.gps = pitsGPS(when_new_position=None, when_lock_changed=None)
        elif board =="dragino":
            self.gps = draginoGPS(when_new_position=None, when_lock_changed=None)

    def __process_gps(self, s):
        self.gps.__process_gps(self,s)

    def _ServerRunning(self):
        self.gps._ServerRunning()

    def _StartServer(self):
        self.gps._StartServer()

    def __doGPS(self, host, port):
        self.gps.__doGPS()

    def __gps_thread(self):
        self.gps.__gps_thread

    def position(self):
        return self.gps.position()
        
    @property
    def time(self):
        return self.gps._GPSPosition['time']

    @property
    def lat(self):
        return self.gps._GPSPosition['lat']
            
    @property
    def lon(self):
        return self.gps._GPSPosition['lon']
            
    @property
    def alt(self):
        return self.gps._GPSPosition['alt']
            
    @property
    def sats(self):
        return self.gps._GPSPosition['sats']
            
    @property
    def fix(self):
        return self.gps._GPSPosition['fix']

    

class pitsGPS(object):
    """
    Gets position from UBlox GPS receiver, using external program for s/w i2c to GPIO pins
    Provides callbacks on change of state (e.g. lock attained, lock lost, new position received)
    """
    PortOpen = False
    
    def __init__(self, when_new_position=None, when_lock_changed=None):
        print("init")
        self._WhenLockChanged = when_lock_changed
        self._WhenNewPosition = when_new_position
        self._GotLock = False
        self._GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0, 'fix': 0}
        self._GPSPositionObject = GPSPosition()
        
        # Start thread to talk to GPS program
        t = threading.Thread(target=self.__gps_thread)
        t.daemon = True
        t.start()
        
    def __process_gps(self, s):
        while 1:
            reply = s.recv(4096)                     
            if reply:
                inputstring = reply.split(b'\n')
                for line in inputstring:
                    if line:
                        temp = line.decode('utf-8')
                        j = json.loads(temp)
                        self._GPSPosition = j
                        if self._WhenNewPosition:
                            self._WhenNewPosition(self._GPSPosition)
                        GotLock = self._GPSPosition['fix'] >= 1
                        if GotLock != self._GotLock:
                            self._GotLock = GotLock
                            if self._WhenLockChanged:
                                self._WhenLockChanged(GotLock)
            else:
                sleep(1)
            
        s.close()
    
    def _ServerRunning(self):
        return "gps" in [psutil.Process(i).name() for i in psutil.pids()]
        
    def _StartServer(self):
        system("pytrack-gps > /dev/null &")
        sleep(1)
        
    def __doGPS(self, host, port):
        try:        
            # Connect socket to GPS server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect((host, port))                     
            self.__process_gps(s)
            s.close()
        except:
            # Start GPS server if it's not running
            if not self._ServerRunning():
                self._StartServer()
        
    def __gps_thread(self):
        host = '127.0.0.1'
        port = 6005
        
        while 1:
            self.__doGPS(host, port)

                    
    def position(self):
        """returns the current GPS position as a dictionary, containing the latest GPS data ('time', 'lat', 'lon', alt', 'sats', 'fix').
        These values can be access individually using the properties below (see the descriptions for return types etc.).
        """
        self._GPSPositionObject.GPSPosition = self._GPSPosition
        return self._GPSPositionObject

        
    @property
    def time(self):
        """Returns latest GPS time (UTC)"""
        return self._GPSPosition['time']
            
    @property
    def lat(self):
        """Returns latest GPS latitude"""
        return self._GPSPosition['lat']
            
    @property
    def lon(self):
        """Returns latest GPS longitude"""
        return self._GPSPosition['lon']
            
    @property
    def alt(self):
        """Returns latest GPS altitude"""
        return self._GPSPosition['alt']
            
    @property
    def sats(self):
        """Returns latest GPS satellite count.  Needs at least 4 satellites for a 3D position"""
        return self._GPSPosition['sats']
            
    @property
    def fix(self):
        """Returns a number >=1 for a fix, or 0 for no fix"""
        return self._GPSPosition['fix']
            

class draginoGPS(object):
    """
    *****Gets position from UBlox GPS receiver, using external program for s/w i2c to GPIO pins
    Provides callbacks on change of state (e.g. lock attained, lock lost, new position received)*****
    """
    PortOpen = False
    
    def __init__(self, when_new_position=None, when_lock_changed=None):
        print("init")
        self._WhenLockChanged = when_lock_changed
        self._WhenNewPosition = when_new_position
        self._GotLock = False
        self._GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0, 'fix': 0}
        self._GPSPositionObject = GPSPosition()
        self._datastream = serial.Serial("/dev/serial0",9600,timeout=0.5)
        
        # Start thread to talk to GPS program
        t = threading.Thread(target=self.__gps_thread)
        t.daemon = True
        t.start()
        
#       def __process_gps(self, s):
#           while 1:
#               reply = s.recv(4096)                     
#               if reply:
#                   inputstring = reply.split(b'\n')
#                   for line in inputstring:
#                       if line:
#                           temp = line.decode('utf-8')
#                           j = json.loads(temp)
#                           self._GPSPosition = j
#                           if self._WhenNewPosition:
#                               self._WhenNewPosition(self._GPSPosition)
#                           GotLock = self._GPSPosition['fix'] >= 1
#                           if GotLock != self._GotLock:
#                               self._GotLock = GotLock
#                               if self._WhenLockChanged:
#                                   self._WhenLockChanged(GotLock)
#               else:
#                   sleep(1)
#               
#           s.close()
#       
#       def _ServerRunning(self):
#           return "gps" in [psutil.Process(i).name() for i in psutil.pids()]
#           
#       def _StartServer(self):
#           system("pytrack-gps > /dev/null &")
#           sleep(1)
#           
#       def __doGPS(self, host, port):
#           try:        
#               # Connect socket to GPS server
#               s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#               s.connect((host, port))                     
#               self.__process_gps(s)
#               s.close()
#           except:
#               # Start GPS server if it's not running
#               if not self._ServerRunning():
#                   self._StartServer()
    def checksum(self,sentence):
        """
        Takes a valid NMEA sentence as a parameter, the checksum is then striped and compared to the remainder of the sentence.
        If the checksum can't be extracted or is invalid then 'False' is returned, if the checksum matches then the function returns 'True'.
        """
        sentence = sentence.rstrip('\n').lstrip('$')
        try: 
            data,cs1 = re.split('\*', sentence)
        except ValueError:
            print("error")
    
        cs2 = 0
        for c in data:
            cs2 ^= ord(c)

        if int(cs1,16)==cs2:
            return True
        else:
            return False
    

    def nmeaToDec(self,dm,dir):
        """
        Converts a NMEA formatted position to a position in Decimal notation.
        """
        if not dm or dm == '':
            return 0.
        match = re.match(r'^(\d+)(\d\d\.\d+)$', dm) 
        if match:
            d, m = match.groups()
        if dir == "W":
            sign = -1
        else:
            sign = 1
        return (float(d) + float(m) / 60)*sign


    def altCheck(self,alt):
        """
        Checks for a valid alt and 
        """
        if not alt or alt == '':
            return 0.
        else :
            return float(alt)


    def parseGGA(self,ggaString):
        rawList = ggaString.split(",")
#        print(rawList)
        time = rawList[1][0:2]+":"+rawList[1][2:4]+":"+rawList[1][4:6]

        if time != "::":
            self._GPSPosition["time"] = time
            self._GPSPosition["fix"]=rawList[6]
            self._GPSPosition["sats"]=int(rawList[7])
            self._GPSPosition["alt"]=self.altCheck(rawList[9])
            self._GPSPosition["lon"]=self.nmeaToDec(rawList[4],rawList[5])
            self._GPSPosition["lat"]= self.nmeaToDec(rawList[2],rawList[3])








    def __gps_thread(self):
        while True:
            byteSentence = self._datastream.readline()
            try:
                nmeaSentence = byteSentence.decode("utf-8")
            except:
                nmeaSentence = "Decode Error"
            if nmeaSentence[3:6] == "GGA":
                if self.checksum(nmeaSentence):
                    self.parseGGA(nmeaSentence)





        
    #            if nmeaSentence[3:6] == "GGA":

     #               if self.checksum(nmeaSentence):
      #                  self._gpsData = self.parseGGA(nmeaSentence)
            sleep(0.2)


                    
    def position(self):
        """returns the current GPS position as a dictionary, containing the latest GPS data ('time', 'lat', 'lon', alt', 'sats', 'fix').
        These values can be access individually using the properties below (see the descriptions for return types etc.).
        """
        self._GPSPositionObject.GPSPosition = self._GPSPosition
        return self._GPSPositionObject

        
    @property
    def time(self):
        """Returns latest GPS time (UTC)"""
        return self._GPSPosition['time']
            
    @property
    def lat(self):
        """Returns latest GPS latitude"""
        return self._GPSPosition['lat']
            
    @property
    def lon(self):
        """Returns latest GPS longitude"""
        return self._GPSPosition['lon']
            
    @property
    def alt(self):
        """Returns latest GPS altitude"""
        return self._GPSPosition['alt']
            
    @property
    def sats(self):
        """Returns latest GPS satellite count.  Needs at least 4 satellites for a 3D position"""
        return self._GPSPosition['sats']
            
    @property
    def fix(self):
        """Returns a number >=1 for a fix, or 0 for no fix"""
        return self._GPSPosition['fix']

