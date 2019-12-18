#YOU NEED TO INSTALL THIS BEFORE LAUNCHING THE SCRIPT !!!
# sudo pip install scapy
import sys
import threading
import os, time
import random
from scapy.all import *
import datetime

##### YOU NEED TO CHANGE THIS ######
interface_default = "wlan0"
if len(sys.argv) > 3 and sys.argv[2] == "-i":
    interface_default = sys.argv[3] #pour your  wifi card interface, need to be in monitor
    print("Interface : "+interface_default)

clear = lambda: os.system('clear')

class Device: #Represent a device such as a smartphone, computer
    def __init__(self, mac, channel=-1, signal=-400, known_ssids=[], packet=None):
        self.mac = mac # device mac address
        self.channel = channel #the channel in witch the device is communicating
        self.known_ssids = known_ssids #store a list of already encontred ssids
        self.packets = [] #store previous packet received (can be probes or beacons)
        self.packets.append(packet)
        self.signals = [] #store previous signal strength
        self.nb_signal = 3 #the number of previous signal strength we want to keep
        self.createdAt = datetime.datetime.now()
        self.updatedAt = self.createdAt
        if signal > -400 :
            self.signals.append(signal)
        self.ssid = None #for network ssid if the device is a network

    def info(self):
        print(str(self.channel)+" > "+self.mac+"("+str(self.getSignalAverage())+")"+str(self.ssid)+"--"+str(self.known_ssids))
        #print(self.signals)

    def isNetwork(self,ssid):
        if(ssid) : self.ssid = ssid;

    def addSignal(self, signal_strenght):
        self.signals.append(signal_strenght)
        if len(self.signals) > 3 : self.signals.pop(0)
        self.updatedAt = datetime.datetime.now()

    def getSignalAverage(self):
        total = 0
        size = len(self.signals)
        for sig in range(0, size) :
            if self.signals[sig] : total += self.signals[sig]
        return total/size

    def addPacket(self, packet):
        self.packets.append(packet)
        if len(self.packets) > self.nb_signal : self.packets.pop(0)
        self.updatedAt = datetime.datetime.now()

    def addknownSSID(self, ssid):
        if ssid and ssid not in self.known_ssids:
            self.known_ssids.append(ssid)

    def setChannel(self, channel):
        self.channel = channel

    def isActive(self): #return if a device is active or not (recently updated)
        limit = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=5)
        if self.updatedAt > limit:
            return True
        return False

    def getJSON(self, mac=False, channel=False, signal=False, known_ssids=False):
        result = {};
        if mac : result["mac"] = self.mac
        result["last-seen"] = self.updatedAt.strftime('%Y-%m-%d %H:%M:%s')
        if channel : result["channel"] = self.channel
        if signal : result["signal"] = self.getSignalAverage()
        if known_ssids : result["know-ssids"] = self.known_ssids
        return result


class Falcon: #The user interface to manipulate devices and devices
    def __init__(self):
        self.devices = {}
        self.known_mac = {"net":[], "dev":[]}
        self.nb_targets = {"net":0, "dev":0}

    def addDevice(self, device):
        type = "dev"
        if device.ssid : type = "net"
        self.known_mac[type].append(device.mac)
        self.devices[device.mac] = device
        self.nb_targets[type] += 1

    def thisMacIsNetwork(self,mac):
        if mac in self.known_mac["dev"] : self.known_mac["dev"].remove(mac)
        if mac not in self.known_mac["net"] : self.known_mac["net"].append(mac)


    def getDevice(self, mac):
        try:
            if mac in self.known_mac["dev"] or mac in self.known_mac["net"]:
                return self.devices[mac]
        except:
            return None

    def getDevicesQuantity(self, active=False):
        if not active: return len(self.known_mac["dev"]) #return the number of devices excluding network devices
        else:
            nb = 0
            for mac in self.known_mac["dev"]:
                try:
                    if self.devices[mac].isActive() : nb = nb + 1
                except:
                    self.known_mac["dev"].remove(mac)
            return nb

    def getNetworksQuantity(self, active):
        if not active: return len(self.known_mac["net"]) #return the number of devices detected
        else:
            nb = 0
            for mac in self.known_mac["dev"]:
                try:
                    if self.devices[mac].isActive() : nb = nb + 1
                except:
                    self.known_mac["net"].remove(mac)
            return nb



    def isUnknown(self, mac, type="all"):
        if type in ["net","dev","all"]:
            if type == "all" :
                if mac not in self.known_mac["net"] and mac not in self.known_mac["dev"]:
                    return 1
            elif mac not in self.known_mac[type]:
                return 1
            return 0
        return 0

    def generateUI(self): #user interface
        clear()

        print("-"*20)
        print("Devices - "+str(len( self.known_mac["dev"])))

        for mac in self.known_mac["dev"]:
            self.devices[mac].info()

        print("-"*20)
        print("Networks - "+str(len(self.known_mac["net"])))

        for mac in self.known_mac["net"]:
            self.devices[mac].info()



def hopper(iface): #sniffing network channels
    n = 1
    stop_hopper = False
    while not stop_hopper:
        time.sleep(0.30)
        os.system('iwconfig '+iface+' channel '+str(n))
        #print("Current Channel "+str(n))
        dig = int(random.random() * 14)
        if dig != 0 and dig != n:
            n = dig

def finder(pckt): #look for packets
    #findProbesReq(pckt)
    #findBeacons(pckt)
    findDevices(pckt)
    if "-v" in sys.argv:
        F.generateUI()

"""
def findBeacons(pckt): #look for beacons and probes response to find devices
    if pckt.haslayer(Dot11Beacon) or pckt.haslayer(Dot11ProbeResp):
        mac_source =  pckt.getlayer(Dot11).addr2
        addElement(pckt, mac_source,"net")


def findProbesReq(pckt): #look for probes request to find devices
    if pckt.haslayer(Dot11ProbeReq):
        mac_source = pckt.addr2
        addElement(pckt, mac_source,"dev")
"""
def findDevices(pckt):
    #pckt.show()
    if pckt.haslayer(Dot11Beacon) or pckt.haslayer(Dot11ProbeResp):
        mac_source =  pckt.getlayer(Dot11).addr2
        addElement(pckt, mac_source,"net")
    #if pckt.haslayer(Dot11ProbeReq):
    else : #we are supposing by default that others request come from classic devices and not networks
        #if not pckt.haslayer(Dot11ProbeReq):
            #pckt.show()
            #print(pckt.addr2)
        #mac_source = pckt.addr2
        if(pckt.addr2) : addElement(pckt, pckt.addr2,"dev")
        if(pckt.addr3) : addElement(pckt, pckt.addr3,"dev")



def addElement(pckt, mac_source, type="dev"): #add device to the falcon database
    signal_source = pckt.dBm_AntSignal
    ssid = None;
    if F.isUnknown(mac_source):
        if not signal_source : signal_source = -300
        knownSSID = []
        if ssid : knownSSID = [ssid]
        dev = Device(mac=mac_source, signal=signal_source, packet=pckt, channel=pckt[RadioTap].Channel, known_ssids=knownSSID)
        if pckt.getlayer(Dot11Elt) :
            ssid = pckt.getlayer(Dot11Elt).info
            if type == "net" :
                dev.isNetwork(ssid)
        F.addDevice(dev)
    else:
        dev = F.getDevice(mac_source)
        dev.addSignal(signal_source)
        dev.addPacket(pckt)
        dev.setChannel(pckt[RadioTap].Channel)
        if pckt.getlayer(Dot11Elt): #if it's not a network
             ssid = pckt.getlayer(Dot11Elt).info
             dev.addknownSSID(ssid)
             if type == "net" and F.isUnknown(mac_source, "net") and ssid :
                 dev.isNetwork(ssid)
                 F.thisMacIsNetwork(mac_source) # we tell to falcon that we made a mistake, atcually it was a network and not a classic device

"""
def findSSIDfromProbe(pckt):
    if pckt.haslayer(Dot11Elt):
        if pckt.ID == 0:
            print("info:"+str(pckt.info))
            dot11elt = pckt.getlayer(Dot11Elt)
            while dot11elt and dot11elt.ID != "SSID":
                dot11elt = dot11elt.payload.getlayer(Dot11Elt)
            if dot11elt:
              return dot11elt.ID

"""

F_bssids = []    # Found BSSIDs
F = Falcon();

def LaunchFalcon(interface):
    thread = threading.Thread(target=hopper, args=(interface, ), name="hopper")
    thread.daemon = True
    thread.start()

    sniff(iface=interface, prn=finder)

if len(sys.argv) > 1 and str(sys.argv[1]) == "-l":
    LaunchFalcon(interface_default)
