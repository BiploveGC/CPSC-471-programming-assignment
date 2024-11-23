import socket
import sys


# Command line check
if len(sys.argv) < 3:
    print("COMMAND: python cli.py <SERVER_MACHINE> <PORT_NUMBER")
    sys.exit()


# Server address and port
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

# Create a TCP socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
clientSocket.connect((serverName, serverPort))

# Send a message
message = "Hello, Server!"
clientSocket.send(message.encode())

# Close Socket
clientSocket.close()