# coding: utf8
import socket
import sys
import threading
from Falcon.flc import *
import time
import datetime
import random
import json

buffer = {"in":"", "out":""}
requests = [] # request struct : {req_id: request value}
responses = [] # response struct : {req_id, response value}
waitlist = []
req_end_char = "&" #caratère de fin de requête
dateFstring = '%Y-%m-%d %H:%M:%s'

def tostring(data):
    return str(data, 'ascii', 'ignore')


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket):

        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        self.req_ids = []
        self.errors = [] #errors table
        self.wait = True #the client should wait for a response
        self.alive = True #if we have to keep alive the connexion
        self.wannago = False #If the client want to stop sending request
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self):
        print("Connexion de %s %s" % (self.ip, self.port, ))
        try:
            while self.alive:
            	# Receive the data in small chunks and retransmit it
                self.waitForRequest()
                self.waitForResponse()
                print("--------")
        finally:
            self.closeConnexion()


    def waitForRequest(self):
        print("client:")
        print(self.req_ids)
        data = self.clientsocket.recv(2048)
        if data:
            ids = None;
            print("received "+tostring(data)+"")
            ids = self.receive(tostring(data)) #filling the buffer util we got a request --> and receive request ids (might be severals)
            if ids and self.wannago == False:
                self.req_ids += ids  #add other requests for the client (ids is a list)
                if "exit" in ids:
                    self.wannago = True
                    self.req_ids.remove("exit");


    def waitForResponse(self):
        #print("wait for response")
        #self.clientsocket.sendall("wait respones".encode("utf-8"))
        while len(self.req_ids):
            try:
                for response in responses: #if there is an response to the request
                    for id in self.req_ids: #we scan all pending request of the client
                        if id in response: #if we found a response to a request
                            #print("response to req_id:"+id)
                            self.send(response[id]) #we send back the reponse to the client
                            self.wait = False;
                            del response[id]; #we delete the response object
                            self.req_ids.remove(id); #we delete the request id because the response has been sent
                            break
                #time.sleep(1)
            except:
                #time.sleep(1) #wait to second before trying again
                self.alive = True;
        if self.wannago == True:  #si le client veut partir et qu'il n'y a plus de requêtes à traiter
            self.alive = False;
        #time.sleep(1)

    def closeConnexion(self):
        # Clean up the connection
        self.clientsocket.close()
        print("Client déconnecté...")


    def abortRequest(self):
        self.wait = False
        d = datetime.datetime.now()
        response = {"type":"error", "date-time": d.strftime(dateFstring), "errors":self.errors}
        self.send(response)


    def receive(self, data):
        req_ids = []
        id = None;
        for char in data:
            if char != req_end_char : buffer["in"] += char
            else :
                #request = self.makeJSON(self.cleanRequest(buffer["in"]))
                request = self.cleanRequest(buffer["in"])

                if request == "exit": return "exit"

                #print("////Requête : "+str(request))
                id = self.generateId() #need to be generated with random par , ip part and time part
                req_ids.append(id);
                requests.append({"id":id, "value":self.fromJSON(request)})
                buffer["in"] = ""

        if len(req_ids): return req_ids
        return None


    def send(self, data):
        self.clientsocket.sendall(self.toJSON(data).encode('utf-8'))


    def cleanRequest(self, request):
        request = request.replace('\n',"")
        request = request.replace("  "," ")
        return request

    def generateId(self):#generating a unique id to identify a request
        dt = str(datetime.datetime.now())
        id = dt[5:7]+dt[8:10]+dt[11:13]+dt[14:16]+dt[17:19]+dt[20:26]+str(random.randrange(200))
        id = self.ip+"-"+str(self.port)+"-"+id
        return id

    def fromJSON(self, string):
        try:
            return json.loads(string)
        except:
            d = datetime.datetime.now()
            self.errors.append({"code":2, "details":"JSON Error : wrong syntax "});
            self.abortRequest();

    def toJSON(self, object):
        try:
            return json.dumps(object)
        except:
            try:
                return str(object)
            except:
                return '{"type":"error", "errors":[{"code":1, "details":"Not able to return the response"}]}'




class FalconThread(threading.Thread): #the devices scanner thread

    def __init__(self):
        threading.Thread.__init__(self)
        print("Launching Falcon Scanner")

    def run(self): #lancement de falcon
        LaunchFalcon()



class RequestHandlerThread(threading.Thread): #request handler

    def __init__(self):
        threading.Thread.__init__(self)
        self.Types = ["wait", "here", "get"]
        self.dtime = None #the current datetime
        self.request = None #the current request

    def run(self): #traitement du tableau des requêtes et mise de la réponse dans le tableau des reponses
        while True:
            #print("Request handler")
            if len(requests) > 0:
                errors = []
                bad = False
                respond = True
                self.dtime = datetime.datetime.now()
                self.request = requests[0]
                value = self.request["value"]
                req_id = ""
                if 'req-id' in value.keys():
                    req_id = value["req-id"]

                response = {"type":None, "rep-id":requests[0]["id"], "req-id":req_id, "devices":[], "date-time": self.dtime.strftime(dateFstring), "info": {}, "errors": []}
                #print(requests[0])

                response["type"] = "nope" #by default the response is negative

                if value == None :
                    requests.pop(0)
                else:
                    if 'type' not in value.keys():
                        response["errors"].append(self.newError(12,"Request Error: Missing type field"))
                        bad = True
                    elif value["type"] not in self.Types:
                        response["errors"].append(self.newError(13,"Request Error: Wrong request type value"))
                        bad = True

                    if 'devices' not in value.keys():
                        response["errors"].append(self.newError(14,"Request Error: Missing devices field"))
                        bad = True
                    elif value["devices"][0] == None:
                        response["errors"].append(self.newError(15,"Request Error: No device identifier has been given"))
                        bad = True
                    if len(req_id) > 128:
                        response["errors"].append(self.newError(16,"Request Error: too long Request ID"))
                        bad = True

                    if bad == False: #we can handle the request
                        #HERE REQUEST
                        if value["type"] == "here":
                            self.here(value, response)

                        #GET REQUEST
                        if value["type"] == "get":
                            self.get(value, response)

                        #WAIT Request
                        if value["type"] == "wait":
                            if not self.wait(value, response) :
                                requests.append(self.request) #if we weren't able to find a devices and not out of time-range, we put the request in the queue
                                respond = False #dont respond to that request

                    else: response["type"] = "error"

                    if respond == True:
                        try :
                            responses.append({requests[0]["id"]:response})
                            requests.pop(0)
                        except:
                            print("Error while appending the response")
                            #print(responses)

            #else:
                #print("No request pending...")

            #time.sleep(1);

    def newError(self,code, details):
        return {"code":code, "details": details}

    def toDate(self, date_time_str):
        return datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

    def get(self, request, response):
        mac = request["devices"][0]
        print(mac)
        device = F.getDevice(mac)
        if not device: device = F.getNetwork(mac)
        if device :
            response["devices"].append(mac)
            response["info"]["device"] = device.getJSON(mac=True, channel=True, signal=True, know_ssids=True)
            response["type"] = "yep"


    def here(self, request, response):
        macs = request["devices"]
        if macs == ["*"]:
            response["devices"] = ["*"]
            response["info"]["net-quantity"] = F.getNetworksQuantity()
            response["info"]["dev-quantity"] = F.getDevicesQuantity()
            response["info"]["total-quantity"] = F.getQuantity()
        else:
            for mac in macs:
                print(mac)
                device = F.getDevice(mac)
                if not device: device = F.getNetwork(mac)
                if device : response["devices"].append(device.mac)
        if len(response["devices"]): response["type"] = "yep"
        else : response["errors"].append(self.newError(17,"Request Error: No devices found, check the devices identifiers"))


    def wait(self, request, response):
        macs = request["devices"]
        time_range = request["time-range"]
        start = self.toDate(time_range[0])
        end = self.toDate(time_range[1])
        print(start)
        print(end )
        if start < self.dtime and self.dtime < end:
            devices = []
            for mac in macs:
                print(mac)
                device = F.getDevice(mac)
                if not device : device =  F.getNetwork(mac) #si on a pas trouvé dans les devices on cherche dans les hotspots
                if device and device.isActive():
                    response["devices"].append(device.mac)
                    devices.append(device)
            if len(response["devices"]): response["type"] = "yep"
            else : return False
        else:
            response["type"] = "error"
            response["errors"].append(self.newError(18,"Request Error: Out of the time range"))
        return True






tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(("",1111))

newthread = FalconThread()
newthread.start()

newthread = RequestHandlerThread()
newthread.start()

while True:
    tcpsock.listen(10)
    #print( "En écoute...")
    (clientsocket, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsocket)
    newthread.start()
