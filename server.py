# coding: utf8
import socket
import sys
import threading

buffer = {"in":"", "out":""}
requests = [] # request struct : {req_id: request value}
responses = [] # response struct : {req_id, response value}
req_end_char = "&" #caratère de fin de requête

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
            while True:
                data = self.clientsocket.recv(2048)
                print("received "+str(data)+"'")
                if data:
                    receive(data)
                    print("sending data back to the client")
                    self.clientsocket.sendall(data)
                else:
                    print("No more data")
                    break
        finally:
            # Clean up the connection
            self.clientsocket.close()    
            print("Client déconnecté...")
            
def receive(data):
    for char in str(str(data).encode("utf-8")):
        if char != req_end_char : buffer["in"] += char
        else :
            print("////Requête : "+cleanRequest(str(buffer["in"])))
            req_id = 15;#ned to be generated with random par , ip part and time part
            requests.append({req_id:cleanRequest(buffer["in"])})
            buffer["in"] = ""
            return req_id
    return None
    
def cleanRequest(request):
    request = request.replace('\n',"")
    request = request.replace("  "," ")
    return request
    
    

class ResponderThread(threading.Thread):

    def __init__(self, ip, port, clientsocket):
        
        threading.Thread.__init__(self)
        #lauching FALCON thread

    def run(self):
        while True:
            print("Holding the request :"+request)
            #request holding here
            # Falcon
            
            #responses.append({req_id, response})
    
	   

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(("",1111))

while True:
    tcpsock.listen(10)
    print( "En écoute...")
    (clientsocket, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsocket)
    newthread.start()
