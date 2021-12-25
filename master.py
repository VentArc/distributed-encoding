import os
import socket
MASTER_IP = "10.0.0.3"

class Machine:
    def __init__(self, name):
        self.name = name
        self.tunnel = socket.socket()
        self.alive = False

    def connect(self, port=34324):
        self.tunnel.bind((MASTER_IP,port))
        self.tunnel.listen(1)
        self.tunnel,address = self.tunnel.accept()
        self.alive = True
        print(address)
    
    def send(self, command):
        print("testing this shit > ")
        # command = input()
        self.tunnel.send(command.encode())
        
    def recv(self):
        print(self.tunnel.recv(444444).decode())





batchToRender = os.scandir()

alpha = Machine("alpha")
alpha.connect()
alpha.send("echo helloworld!")
alpha.recv()

# establish connection to other renderers


# for fileToRender in batchToRender:
#     #split it up