#bluetooth
import pexpect
import requests
import time
import threading

btAddrs = []
child = pexpect.spawn('sudo bluetoothctl')
def GetBlueTooth():
    child.send("scan on\n")
    

    while True:
            try:
                #print("\n---------------------------\n")
                print("GetBlueTooth is running...")
                child.expect("Device (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")
                btAddr = child.match.group(1)
                if btAddr not in btAddrs:
                    btAddrs.append(btAddr)
                    print(btAddr)
                #child.expect("Device (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")
                #print(child.match.group(1))
                #print("now have {}\n".format(btAddrs))
            except:
                print "Something wrong in GetBlueTooth()!!!"



t1 = threading.Thread(target=GetBlueTooth)
t1.start()

time.sleep(30)
print("===========================")
for i in range(0, len(btAddrs)):
    child.send("remove {}".format(btAddrs[i]))
print("===========================")
child.send("exit")
child = pexpect.spawn('sudo bluetoothctl')
child.send("scan on\n")
child.expect("Device (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")
print(child.match.group(1))
child.expect("Device (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")
print(child.match.group(1))
child.expect("Device (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")
print(child.match.group(1))
