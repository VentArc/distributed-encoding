import os
import socket
import struct
import enum
import subprocess
import math
MASTER_IP = "10.0.0.3"

# Protocol:
# uint32 := msgLength
# uint32 := msgType
# bytes  := msgContent

# def binarySearch(a, b, function):
#     print(a, b, function(a,b))
#     if function(a, b) == 0:
#         return a
#     if function(a, b) == -1:
#         return binarySearch(a, b/2, function)
#     if function(a, b) == 1:
#         return binarySearch((b/2)+a, b, function)

# def betweenMinute(a, b):
#     if b-a < 0.0001: # caso base epsilon
#         return 0
#     if a < 0.0000000001: a = 0.0000000001
#     if b-a < 60:
#         return -1
#     else:
#         return 1

class TimeManager:
    def __init__(self, dateformat) -> None:
        sec = float(dateformat[-5:])
        min = int(dateformat[-8:-6]) * 60
        hour = int(dateformat[:-9])  * 60 * 60
        self.sec = sec + min + hour       

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

class Video:
    def __init__(self, file) -> None:
        self.file = file
        probe = subprocess.run(["ffprobe", file], capture_output=True).stderr.decode()
        self.duration = TimeManager(probe[probe.find("Duration: ") + len("Duration: ") : probe.find("Duration: ") + len("Duration: ") + 11]).sec
        self.fps = int(probe[probe.find(" fps,")-3 : probe.find(" fps,")])
        self.clipTime = 2700 / self.fps
        self.numberClips = self.duration / self.clipTime

    

print(Video("Big Buck Bunny Demo.mp4").duration, Video("Big Buck Bunny Demo.mp4").clipTime, Video("Big Buck Bunny Demo.mp4").numberClips)
v = Video("Big Buck Bunny Demo.mp4")
for nclip in range(math.ceil(v.numberClips)):
    if (v.clipTime * (nclip + 1)) > v.duration:
        print(f"{v.clipTime * nclip} => {v.duration}")
    else:
        print(f"{v.clipTime * nclip} => {v.clipTime * (1 + nclip)}")        

# print((Message(MessageFormat(1),"test")).format == MessageFormat.command)
# print(MessageFormat(1).value)

# batchToRender = os.scandir()

# alpha = Machine("alpha")
# alpha.connect()
# alpha.send(Message(MessageFormat(1),bytes("echo helloworld!", 'utf-8')))
# alpha.recv()

# establish connection to other renderers


# for fileToRender in batchToRender:
#     #split it up