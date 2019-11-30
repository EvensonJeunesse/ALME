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

def tostring(data):
    return str(data, 'ascii', 'ignore')


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket):

        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

    def run(self):

        print("Connexion de %s %s" % (self.ip, self.port, ))
        try:
    	# Receive the data in small chunks and retransmit it
            req_id = None
            while not req_id: #waiting for the complete request
                data = self.clientsocket.recv(2048)
                print("received "+tostring(data)+"")
                if data:
                    req_id = self.receive(tostring(data))
                    print("sending data back to the client")
                    self.clientsocket.sendall(data)
                else:
                    print("No more data")
                    break
            while True: ## Waiting for the response
                response = "We are holding your request"
                print(requests)
                self.clientsocket.sendall(response.encode('utf-8'))
                time.sleep(10);

        finally:
            # Clean up the connection
            self.clientsocket.close()
            print("Client déconnecté...")

    def receive(self, data):
        for char in data:
            if char != req_end_char : buffer["in"] += char
            else :
                #request = self.makeJSON(self.cleanRequest(buffer["in"]))
                request = self.cleanRequest(buffer["in"])
                print("////Requête : "+str(request))
                req_id = self.generateId();#ned to be generated with random par , ip part and time part

                requests.append({req_id:request})
                buffer["in"] = ""
                return req_id
        return None



    def cleanRequest(self, request):
        request = request.replace('\n',"")
        request = request.replace("  "," ")
        return request

    def generateId(self):#generating a unique id to identify a request
        dt = str(datetime.datetime.now())
        id = dt[5:7]+dt[8:10]+dt[11:13]+dt[14:16]+dt[17:19]+dt[20:26]+str(random.randrange(200))
        id = self.ip+"-"+str(self.port)+"-"+id
        return id

    def makeJSON(self, request_str):
        return json.loads(request_str)




class FalconThread(threading.Thread): #the devices scanner thread

    def __init__(self):
        threading.Thread.__init__(self)
        print("Launching Falcon Scanner")

    def run(self): #lancement de falcon
        LaunchFalcon()



class RequestHandlerThread(threading.Thread): #request handler

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self): #traitement du tableau des requêtes et mise de la réponse dans le tableau des reponses
        while True:
            print("Request handler")
            print(requests)
            time.sleep(3);





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
