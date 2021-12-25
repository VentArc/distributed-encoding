import os
import socket


class Machine:
    def __init__(self, name):
        self.name = name
        self.tunnel = socket.socket()
        self.alive = False

    def connect(self, ip, port=34324):
        self.tunnel.bind((ip,port))
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
alpha.send("echo helloworld!")
alpha.recv()

# establish connection to other renderers


# for fileToRender in batchToRender:
#     #split it up