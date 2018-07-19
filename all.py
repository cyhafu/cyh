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
import pexpect
import requests
#server & db
import json
import requests

temp = -1
hum = -1
lat = -99
lng = -99
btAddrs = []
jsonobj = {"Watch": []}


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
            time.sleep(2)
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
                time.sleep(2)
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
    child = pexpect.spawn('sudo bluetoothctl')
    child.send("scan on\n")
    

    while True:
            try:
                #print("\n---------------------------\n")
                print("GetBlueTooth is running...")
                time.sleep(2)
                child.expect("Device (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")
                btAddr = child.match.group(1)
                if btAddr not in btAddrs:
                    btAddrs.append(btAddr)
                    jsonobj["Watch"].append(dict(addr=btAddr))
                    #print(btAddr)
            except:
                print "Something wrong in GetBlueTooth()!!!"

def GetAndSendAllData():
    global temp, hum, lat, lng
    i = 0
    
    while True:
        try:
            time.sleep(10)
            
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












    
    
