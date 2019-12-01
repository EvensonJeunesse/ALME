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
        self.errors = [] #errors table
        self.wait = True #the client should wait for a response
        self.alive = True #if we have to keep waiting for request
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self):
        print("Connexion de %s %s" % (self.ip, self.port, ))
        try:
            while self.alive:
            	# Receive the data in small chunks and retransmit it
                self.waitForRequest()
                self.waitForResponse()
        finally:
            self.closeConnexion()


    def waitForRequest(self):
        self.req_id = None
        while not self.req_id: #waiting for the complete request
            data = self.clientsocket.recv(2048)
            if data:
                print("received "+tostring(data)+"")
                self.req_id = self.receive(tostring(data)) #filling the buffer util we got a request --> and receive a request id
            if self.req_id == "exit":
                self.wait = False
                self.alive = False
                break

    def waitForResponse(self):
        self.clientsocket.sendall("wait respones".encode("utf-8"))
        while self.wait: ## Waiting for the response
            try:
                for response in responses: #if there is an response to the request
                    if self.req_id in response.key() : self.send(response[self.req_id]) #we send back the reponse to the client
                    break
            except:
                time.sleep(2) #wait to second before trying again

    def closeConnexion(self):
        # Clean up the connection
        self.clientsocket.close()
        print("Client déconnecté...")


    def abortRequest(self):
        self.wait = False
        d = datetime.datetime.now()
        response = {"type":"nope", "date-time": d.strftime(dateFstring), "errors":self.errors}
        self.send(response)


    def receive(self, data):
        for char in data:
            if char != req_end_char : buffer["in"] += char
            else :
                #request = self.makeJSON(self.cleanRequest(buffer["in"]))
                request = self.cleanRequest(buffer["in"])

                if request == "exit": return "exit"

                print("////Requête : "+str(request))
                req_id = self.generateId();#ned to be generated with random par , ip part and time part
                requests.append({"id":req_id, "value":self.fromJSON(request)})
                buffer["in"] = ""
                return req_id
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
                return '{"type":"nope", "errors":[{"code":1, "details":"Not able to return the response"}]}'




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

    def run(self): #traitement du tableau des requêtes et mise de la réponse dans le tableau des reponses
        while True:
            print("Request handler")
            if len(requests) > 0:
                d = datetime.datetime.now()
                response = {"type":None, "date-time": d.strftime(dateFstring), "info": {}, "errors": []}
                req = {"type":None, "devices":[], "info":None, "time-range":{}}
                errors = []
                bad = False
                value = requests[0]["value"]
                print(requests[0])

                if value == None :
                    requests.pop(0)
                    break


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


                if bad :
                    response["type"]="nope"
                    #try :
                    responses.append({requests[0]["id"]:response})
                    requests.pop(0)
                    #except:
                    print("Error while appending the response")
                    print(responses)

            else:
                print("No request pending...")

            time.sleep(3);

    def newError(self,code, details):
        return {"code":code, "details": details}




tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(("",1111))

newthread = FalconThread()
newthread.start()

newthread = RequestHandlerThread()
newthread.start()

while True:
    tcpsock.listen(10)
    print( "En écoute...")
    (clientsocket, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsocket)
    newthread.start()
