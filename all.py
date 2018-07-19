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


temp = -1
hum = -1
lat = -99
lng = -99
jsonobj = {}


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
        while True:
            try:
                #print("\n---------------------------\n")
                print("GetGPS is running...")
                time.sleep(4)
                #print 'latitude    ' , gpsd.fix.latitude
                #print 'longitude   ' , gpsd.fix.longitude
                #print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time
                global lat
                global lng
                lat = gpsd.fix.latitude
                lng = gpsd.fix.longitude
            except : 
                print "Something wrong in GetGPS()!!!"
                

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
          jsonobj['Watch'] = watchobj
          #print('obj')
          #print(jsonobj)
    except:
      print "Something wrong in GetBlueTooth()!!!"
      

def GetAndSendAllData():
    global temp, hum, lat, lng
    i = 0
    time.sleep(10)
    
    while True:
        try:
            time.sleep(8)
            
            jsonobj['lat'] = repr(lat)
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
        except:
            print("Something wrong in GetAndSendAllData()!!!")

            
        


    

#GetTemp();
#GetGPS();
#GetBlueTooth();
print("Geting Start...")
print('open Bluetooth device')
subprocess.call(['systemctl', 'start', 'hciuart'])

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












    
    
