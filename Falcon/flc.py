#YOU NEED TO INSTALL THIS BEFORE LAUNCHING THE SCRIPT !!!
# sudo pip install scapy
import threading
import os, time
import random
from scapy.all import *

##### YOU NEED TO CHANGE THIS ######
interface = "wlp5s0" #pour your  wifi card interface, need to be in monitor mode






clear = lambda: os.system('clear')

class Device: #Represent a device such as a smartphone, computer
    def __init__(self, mac, channel=-1, signal=-400, know_ssids=[], packet=None):
        self.mac = mac # device mac address
        self.channel = channel #the channel in witch the device is communicating
        self.know_ssids = know_ssids #store a list of already encontred ssids
        self.packets = []; #store previous packet received (can be probes or beacons)
        self.packets.append(packet)
        self.signals = [] #store previous signal strength
        self.nb_signal = 3; #the number of previous signal strength we want to keep
        if signal > -400 :
            self.signals.append(signal)

    def info(self):
        print(str(self.channel)+" > "+self.mac+"("+str(self.getSignalAverage())+")")
        #print(self.signals)

    def addSignal(self, signal_strenght):
        self.signals.append(signal_strenght)
        if len(self.signals) > 3 : self.signals.pop(0)

    def getSignalAverage(self):
        total = 0
        size = len(self.signals)
        for sig in range(0, size) :
            total += self.signals[sig]
        return total/size

    def addPacket(self, packet):
        self.packets.append(packet)
        if len(self.packets) > self.nb_signal : self.packets.pop(0)

    def setChannel(self, channel):
        self.channel = channel

class Network(Device): #Reprensent an Wifi network, it is a special device
    def __init__(self, ssid, mac, channel=-1, signal=-400, packet=None):
        super().__init__(mac, channel, signal)
        self.ssid = ssid

    def info(self):
        print(str(self.channel)+" > "+str(self.ssid)+" "+self.mac+"("+str(self.getSignalAverage())+")")

class Falcon: #The user interface to manipulate devices and networks
    def __init__(self):
        self.devices = {}
        self.networks = {}
        self.known_mac = {"net":[], "dev":[]}
        self.nb_targets = {"net":0, "dev":0}

    def addDevice(self, device):
        self.known_mac["dev"].append(device.mac)
        self.devices[device.mac] = device
        self.nb_targets["dev"] += 1

    def getDevice(self, mac):
        return self.devices[mac]

    def addNetwork(self, network):
        self.known_mac["net"].append(network.mac)
        self.networks[network.mac] = network
        self.nb_targets["net"] += 1

    def getNetwork(self, mac):
        return self.networks[mac]

    def isUnknown(self, mac, type):
        if type in ["net","dev"]:
            if mac not in self.known_mac[type]:
                return 1
            return 0
        return 0

    def generateUI(self): #user interface
        clear()
        #patern = "{:>20}"
        """for net in self.networks:
            print(str(self.networks[net].info()))"""


        print("-"*20)
        print("Devices - "+str(len(self.devices)))

        for dev in self.devices:
            self.devices[dev].info()

        print("-"*20)
        print("Networks - "+str(len(self.networks)))

        for net in self.networks:
            self.networks[net].info()



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

def finder(pckt):
    findProbesReq(pckt)
    findBeacons(pckt)
    #F.generateUI()


def findBeacons(pckt):
    if pckt.haslayer(Dot11Beacon) or pckt.haslayer(Dot11ProbeResp):
        mac_source =  pckt.getlayer(Dot11).addr2
        signal_source = pckt.dBm_AntSignal
        if F.isUnknown(mac_source, type="net"):
            ssid = pckt.getlayer(Dot11Elt).info
            net = Network(ssid=ssid,mac=mac_source, signal=signal_source, packet=pckt, channel=pckt[RadioTap].Channel)
            F.addNetwork(net)
        else:
            net = F.getNetwork(mac_source)
            net.addSignal(signal_source)
            net.addPacket(pckt)
            net.setChannel(pckt[RadioTap].Channel)
        #net.info()


def findProbesReq(pckt):
    if pckt.haslayer(Dot11ProbeReq):
        mac_source = pckt.addr2
        signal_source = pckt.dBm_AntSignal
        if F.isUnknown(mac_source, type="dev") :
            #print(pckt.show())
            dev = Device(mac=pckt.addr2, signal=signal_source, packet=pckt, channel=pckt[RadioTap].Channel)
            F.addDevice(dev)
        else :
            dev = F.getDevice(mac_source)
            dev.addSignal(signal_source)
            dev.addPacket(pckt)
            dev.setChannel(pckt[RadioTap].Channel)
        #dev.info()


F_bssids = []    # Found BSSIDs
F = Falcon();

def LaunchFalcon():
    thread = threading.Thread(target=hopper, args=(interface, ), name="hopper")
    thread.daemon = True
    thread.start()

    sniff(iface=interface, prn=finder)



"""
if __name__ == "__main__":

    thread = threading.Thread(target=hopper, args=(interface, ), name="hopper")
    thread.daemon = True
    thread.start()

    sniff(iface=interface, prn=finder)
"""
