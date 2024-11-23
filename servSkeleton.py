# SOCKET COMMANDS
# 1. https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python
# 2. https://docs.python.org/3/library/socket.html


# Allows to create and work with network sockets
import socket
import sys



# Command line check
if len(sys.argv) < 2:
    print("COMMAND: python3 serv.py <PORT_NUMBER>")
    sys.exit()



# Get the port number from the command line
serverPort = int(sys.argv[1])

# Create TCP socket
# 1. socket.AF_INET: Address Family - Internet used for IPv4
# 2. socket.SOCK_STREAM: Indicates socket will use TCP protocol
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to a port
serverSocket.bind(('', serverPort))

# Start listening on socket
serverSocket.listen(1)
print(f"Server is listening on port {serverPort}...")


# Accept connections forever (revieve data from client)
while True:
    # Accept a new connection
    connectionSocket, clientAddr = serverSocket.accept()
    print(f"Accepted connection from {clientAddr}")

    # For now, we'll just receive a message and close
    data = connectionSocket.recv(4096).decode()
    print(f"Recieved data: {data}")

    # Close client connection
    connectionSocket.close()

