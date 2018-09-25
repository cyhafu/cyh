#os
import time
import threading
#temp
import sys
import Adafruit_DHT
#GPS
import os
from gps import *
from time import *
import time
#bluetooth
import subprocess
import pexpect
import requests
#server & db
import json
import requests
#gps distance
from math import radians, cos, sin, asin, sqrt
#sms
import commands
#date time
import datetime  


temp = -1
hum = -1
lat = -99
lng = -99
lat2 = -99
lng2 = -99
jsonobj = {}

#for check student is out of car
watchArray = []
valueInWatchArray = [] #0=>78++
lat_1stMeetWatchArray = []
lng_1stMeetWatchArray = []



#===============bluetooth class==========================================
class BluetoothctlError(Exception):
    """This exception is raised, when bluetoothctl fails to start."""
    pass


class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""

    def __init__(self):
        out = subprocess.check_output("rfkill unblock bluetooth", shell = True)
        self.child = pexpect.spawn("bluetoothctl", echo = False)

    def get_output(self, command, pause = 0):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.child.send(command + "\n")
        time.sleep(pause)
        start_failed = self.child.expect(["bluetooth", pexpect.EOF])

        if start_failed:
            raise BluetoothctlError("Bluetoothctl failed after running " + command)

        return self.child.before.split("\r\n")

    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            out = self.get_output("scan on")
        except BluetoothctlError, e:
            print(e)
            return None

    def make_discoverable(self):
        """Make device discoverable."""
        try:
            out = self.get_output("discoverable on")
        except BluetoothctlError, e:
            print(e)
            return None

    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = not any(keyword in info_string for keyword in block_list)

        if string_valid:
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2]
                    }

        return device

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        try:
            out = self.get_output("devices")
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            available_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)

            return available_devices

    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        try:
            out = self.get_output("paired-devices")
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            paired_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)

            return paired_devices

    def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()

        return [d for d in available if d not in paired]

    def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = self.get_output("info " + mac_address)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            return out

    def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            out = self.get_output("pair " + mac_address, 4)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to pair", "Pairing successful", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            out = self.get_output("remove " + mac_address, 3)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            res = self.child.expect(["not available", "Device has been removed", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            out = self.get_output("connect " + mac_address, 2)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to connect", "Connection successful", pexpect.EOF])
            success = True if res == 1 else False
            return success

    def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            out = self.get_output("disconnect " + mac_address, 2)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to disconnect", "Successful disconnected", pexpect.EOF])
            success = True if res == 1 else False
            return success
#========================================================================

#--------------temp Var--------------------------
sensor = Adafruit_DHT.DHT22
pin = 4
#------------------------------------------------

#--------------gps Var and Class-----------------
gpsd = None

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd 
    gpsd = gps(mode=WATCH_ENABLE) 
    self.current_value = None
    self.running = True
    
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next()

if __name__ == '__main__':
        gpsp = GpsPoller()
#------------------------------------------------

def isHaveinWatchArray(_1watchCheck):
    global watchArray
    for x in range(len(watchArray)):
       # print "============="
        #print "check btw :"
        #print _1watchCheck
        #print watchArray[x]
        #print "============="
        if _1watchCheck == watchArray[x]: 
            return True
    return False

def CountUpForNotFoundWatch(watchFounds):
    global watchArray
    for x in range(len(watchFounds)):
        if isHaveinWatchArray(watchFounds[x]):
            print "============="
            print "found "
            print watchFounds[x]
            print "============="

def GetWatchMacAddr():
    global watchArray
    print "GetWatchMacAddr ..."
    r = requests.get("https://kiddatabase.herokuapp.com/getbandincar")
    data = r.json()
    for x in range(len(data[0]['watch'])):
        #print data[0]['watch'][x]['mac_address']
        watchArray.append(data[0]['watch'][x]['mac_address'])
        valueInWatchArray.append(0)
        
    print "len of watchArray is : "
    print len(watchArray)
    print watchArray
    print "value is : "
    print valueInWatchArray
    

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km


def sendsms(message, target):
    commandString = 'sudo gammu sendsms TEXT '+target+' -textutf8 "'+message+'"'
    print commands.getoutput(commandString)

def GetTemp():
    while True:
        try:
            #print("\n---------------------------\n")
            print("GetTemp is running...")
            time.sleep(4)
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            if humidity is not None and temperature is not None:
                #print 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
                global temp
                global hum
                temp = temperature
                hum = humidity
            else:
                print 'Failed to get reading temp & hum. Try again!'
        except:
            print "Something wrong in GetTemp()!!!"
    


def GetGPS():
    
        gpsp.start()
        count = 0
        gpsCount = 0
        while True:
            try:
                if count >= 10:
                    subprocess.call(['sudo', 'killall', 'gpsd'])
                    count = 0
                #print("\n---------------------------\n")
                print("GetGPS is running...")
                time.sleep(4)
                #print 'latitude    ' , gpsd.fix.latitude
                #print 'longitude   ' , gpsd.fix.longitude
                #print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time
                global lat, lat2
                global lng, lng2
                if gpsCount == 0:
                    lat = gpsd.fix.latitude
                    lng = gpsd.fix.longitude
                    lat2 = gpsd.fix.latitude
                    lng2 = gpsd.fix.longitude
                else:
                    lat2 = lat
                    lng2 = lng 
                    lat = gpsd.fix.latitude
                    lng = gpsd.fix.longitude
                
                if lat == "nan" or lng == "nan" :
                    count = count + 1

                gpsCount = gpsCount+1
            except : 
                print "Something wrong in GetGPS()!!!"
                count = count + 1
                

def GetBlueTooth():
  watchobj = {}
  while True :
    try:
      if __name__ == "__main__":

          for i in range(0, len(watchobj)) :
              bl.remove(watchobj[i]['mac_address'])
              print ('removed {}'.format(watchobj[i]['mac_address']))

          print ('----- Done Remove -----')
              
          watchobj = {}
          print("Init bluetooth...")
          bl = Bluetoothctl()
          print("Ready!")
          bl.start_scan()
          print("Scanning for 15 seconds...")
          for i in range(0, 15):
              print(i)
              time.sleep(1)

          watchobj = bl.get_discoverable_devices()
          print('@@@ now have {} @@@'.format(str(len(watchobj))))
          #print(watchobj)
          
          for i in range(0, len(watchobj)):
              print "###########info############"
              print watchobj[i]['mac_address']
              ss = str(bl.get_device_info(watchobj[i]['mac_address']))
              #print ss
              pos = ss.find("R")
              #print ("pos is {}".format(str(pos)))
              rr = ss[pos:(pos+9)]
              print rr
              xx = rr.split(' ', 1 )
              print xx[1]
              watchobj[i]['rssi'] = xx[1]
              print watchobj[i]
              
          jsonobj['watch'] = watchobj
          #print jsonobj['watch']
          #s="mystring"
          #s[4:10]
          #print('obj')
          #print(jsonobj)
          
          print "========================================="

    except:
      print "Something wrong in GetBlueTooth()!!!"
      

def GetAndSendAllData():
    global temp, hum, lat, lng, lat2, lng2
    i = 0
    timeCheckCount = 0
    time.sleep(10)
    
    while True:
        try:
            time.sleep(8)
            #38 times to check 3 options mean is "kid stuck in car"
            #have to send sms to parent and driver
            #print ("temp : {}".format(temp))
            #print ("lat : {}".format(lat))
            #print ("lng : {}".format(lng))
            #print ("lat2 : {}".format(lat2))
            #print ("lng2 : {}".format(lng2))

            #!!!!!! stuck in the van !!!!!!!
            print ("distance : {}".format(haversine(lng, lat, lng2, lat2)*1000))
            if temp>=27 and (haversine(lng, lat, lng2, lat2)*1000)<=20:
                timeCheckCount = timeCheckCount+1
                print ("now ms: {}".format((timeCheckCount+1)*8))
            else:
                timeCheckCount = 0

            if timeCheckCount >= 76 :
                print "Help!!!"
                sendsms("hi dad come help me right now, I don't have must time xD!", "+66952586024")
            #=====!!!!!! end stuck in the van !!!!!!=====

            #date time
            dt = str(datetime.datetime.now())
            d = dt.split(' ', 1 )
            s = list(d[0])
            s[4] = '/'
            s[7] = '/'
            dd = "".join(s)
            tt = d[1][:8]
            jsonobj['date'] = dd
            jsonobj['time'] = tt
            jsonobj['lat'] = repr(lat)
            jsonobj['id'] = 'car001'
            jsonobj['lng'] = repr(lng)
            jsonobj['temp'] = repr(temp)
            jsonobj['hum'] = repr(hum)
            
            
            #print("Temp : {}".format(temp))
            #print("Hum : {}".format(hum))
            #print("lat : {}".format(lat))
            #print("lng : {}".format(lng))
            
            print("# {} ".format(i+1))
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
            print("JsonObj : {}".format(jsonobj))
            print("\n--------------------------------------\n")
            r2 = requests.post('https://kiddatabase.herokuapp.com/post',json = jsonobj)
            print (r2.status_code)
            print (r2.text)
            print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
            #bAddrs = []
            i = i+1
            timeCheckCount = timeCheckCount+1
        except:
            print("Something wrong in GetAndSendAllData()!!!")




#GetTemp();
#GetGPS();
#GetBlueTooth();
print("Geting Start...")
print('open Bluetooth device')
subprocess.call(['systemctl', 'start', 'hciuart'])
GetWatchMacAddr()
w = ["F4:A7:65:7B:B7:62", "D8:2A:9A:6F:SA:52"]
CountUpForNotFoundWatch(w)

for i in range(0,10):
    print(".")
    time.sleep(1)

print("@@@ Runing @@@")

t1 = threading.Thread(target=GetTemp)
t2 = threading.Thread(target=GetGPS)
t3 = threading.Thread(target=GetBlueTooth)
t4 = threading.Thread(target=GetAndSendAllData)

t1.start()
t2.start()
t3.start()
t4.start()
