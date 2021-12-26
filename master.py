import os
import socket
import struct
import enum
MASTER_IP = "10.0.0.3"

class MessageFormat(enum.Enum):
    command = 1
    video   = 2

class Message:
    def __init__(self, format: MessageFormat, content):
        self.format = format
        self.content = content

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

    def send(self, msg: Message):
        # struct.pack converts the length of the message in a 4-byte unsigned integer
        msglen = struct.pack('>I', len(msg.content))
        msgtype = struct.pack('>I', msg.format.value)
        msg = msglen + msgtype + msg.content
        
        self.tunnel.sendall(msg)
        print(msg) # debug

    def recv(self) -> Message | None:

        # Helper function to recv n bytes or return None if EOF is hit
        def recvall(socket, n):
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

        # Read message type
        msgtype = recvall(self.tunnel, 4)
        if not msgtype:
            return None
        msgtype = struct.unpack('>I', msgtype)[0]

        # Read the message
        msg = recvall(self.tunnel, msglen)

        # Packs all data in Message class
        return Message(MessageFormat(msgtype, msg))

# protcol 
# the start has a 4-byte length (max message length aprox 4Gb ) then a byte of formatting


# print((Message(MessageFormat(1),"test")).format == MessageFormat.command)
# print(MessageFormat(1).value)

# batchToRender = os.scandir()

alpha = Machine("alpha")
alpha.connect()
alpha.send(Message(MessageFormat(1),bytes("echo helloworld!", 'utf-8')))
alpha.recv()

# establish connection to other renderers


# for fileToRender in batchToRender:
#     #split it up