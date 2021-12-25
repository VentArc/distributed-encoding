import os
import socket
import struct
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
    
    def send(self, msg):
        # struct.pack converts the length of the message in a 4-byte unsigned integer
        msg = struct.pack('>I', len(msg)) + msg 
        self.tunnel.sendall(msg)
        print(msg) # debug

    def recv(self):

        def recvall(socket, n):
            # Helper function to recv n bytes or return None if EOF is hit
            data = bytearray()
            while len(data) < n:
                packet = socket.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            return data

        # Read header message length
        msglen = recvall(self.tunnel, 4) # 4 because of the 4-bytes size prefix
        if not msglen:
            return None
        msglen = struct.unpack('>I', msglen)[0]

        #Read the message
        return recvall(self.tunnel, msglen)

# protcol 
# the start has a 8-byte length (max message length aprox 4Gb )


batchToRender = os.scandir()

alpha = Machine("alpha")
alpha.connect()
alpha.send(bytes("echo helloworld!", 'utf-8'))
alpha.recv()

# establish connection to other renderers


# for fileToRender in batchToRender:
#     #split it up