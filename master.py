import os
import socket
import struct
import enum
import subprocess
import math
from typing import Counter
MASTER_IP = "10.0.0.3"

# Protocol:
# uint32 := msgLength
# uint32 := msgType
# bytes  := msgContent

def timeToSec(dateformat) -> float:
    sec = float(dateformat[-5:])
    min = int(dateformat[-8:-6]) * 60
    hour = int(dateformat[:-9])  * 60 * 60
    return sec + min + hour       

def secToTime(secs) -> str:
    hour = int((secs // (60 * 60)) % (60 *60))
    min  = int((secs // 60) % 60)
    sec  = (secs % 60)
    return f"{hour}:{min}:{sec:.3f}" 

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
        
        # file itself
        self.file = file
        
        # duration related info
        print("Calculating Video Length...", end="\r")
        probe = subprocess.run(["ffprobe", file], capture_output=True).stderr.decode()
        self.duration = timeToSec(probe[probe.find("Duration: ") + len("Duration: ") : probe.find("Duration: ") + len("Duration: ") + 11])
        self.fps = int(probe[probe.find(" fps,")-3 : probe.find(" fps,")])
        self.clipTime = 2700 / self.fps
        self.numberClips = self.duration / self.clipTime
        
        # keyFrames calculation
        comm = ("ffprobe -v error -skip_frame nokey -show_entries frame=pkt_pts_time -select_streams v -of csv=p=0").split()
        comm.append(self.file)
        print("Calculating KeyFrames...", end="\r")
        keyFrames = subprocess.run(comm, capture_output=True).stdout
        keyFrames = keyFrames.decode("utf-8")
        keyFrames = keyFrames.split(sep="\n")
        self.keyFrames = list(filter(None, keyFrames))

        # video splits
        self.splits = []
        indexCurrentKeyFrame = 0
        print("Calculating Splits...", end="\r")
        for split in range(math.ceil(self.numberClips)):
            # Last KeyFrame base-case
            if (self.keyFrames[indexCurrentKeyFrame] == self.keyFrames[-1]):
                break
            epsilon = ((1/self.fps)*1/10)
            start = float(self.keyFrames[indexCurrentKeyFrame]) - epsilon
            self.splits.append([str(start)])
            indexOld = indexCurrentKeyFrame

            while not(float(self.keyFrames[indexCurrentKeyFrame]) > (float(self.keyFrames[indexOld]) + self.clipTime)):
                # Last KeyFrame base-case
                if (self.keyFrames[indexCurrentKeyFrame] == self.keyFrames[-1]):
                    break
                indexCurrentKeyFrame += 1
            end = float(self.keyFrames[indexCurrentKeyFrame]) - epsilon
            self.splits[split].append(str(end))

v = Video("Big Buck Bunny Demo.mp4")
print(v.splits, v.keyFrames[-1])
counter = 0

for split in v.splits:
    exe = subprocess.run(["ffmpeg", "-ss", split[0], "-i", "Big Buck Bunny Demo.mp4", "-to", split[1], "-c:v", "libx264", "-vf", "scale='min(1280,iw)':'min(720,ih)'", f"{counter}.mp4"])
    print(exe)
    counter += 1

# for nclip in range(math.ceil(v.numberClips)):
#     if (v.clipTime * (nclip + 1)) > v.duration:
#         print(f"{v.clipTime * nclip} => {v.duration}")
#         l = list(map(secToTime, [v.clipTime * nclip, v.duration]))
#     else:
#         print(f"{v.clipTime * nclip} => {v.clipTime * (1 + nclip)}")        
#         l = list(map(secToTime, [v.clipTime * nclip, v.clipTime * (1 + nclip)]))
    # exe = subprocess.run(["ffmpeg", "-i", "Big Buck Bunny Demo.mp4", "-ss", l[0], "-to", l[1], "-c", "copy", f"{counter}.mp4"])
    # print(exe)
    # counter += 1
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