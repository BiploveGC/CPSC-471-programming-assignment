# SOCKET COMMANDS
# 1. https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python
# 2. https://docs.python.org/3/library/socket.html

# https://docs.python.org/3/library/os.html
import os
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


# Accept connections forever (recieve data from client)
while True:
    # Accept a new connection
    connectionSocket, clientAddr = serverSocket.accept()
    print(f"Accepted connection from {clientAddr}")

    # Recieve the command from the client
    command = connectionSocket.recv(4096).decode()
    print(f"Recieved data: {command}")


    # Command Section
    # LS 
    if command == "ls":
        try:
            # Run ls command using os.listdir() to list files
            # More info on os at top
            files = os.listdir('.')
            result = "\n".join(files)
            connectionSocket.send(result.encode())
        except Exception as e:
            error_message = f"Error executing ls command: {e}"
            connectionSocket.send(error_message.encode())

    # PUT
    elif command.startswith("put"):
        try:
            # Extract filename
            _, filename = command.split(" ", 1)

            # Receive the size of the file first
            fileSize = int(connectionSocket.recv(4096).decode())

            # Receive actual file data
            fileData = connectionSocket.recv(fileSize)

            # Save the recieved data to a new file
            with open(filename, "wb") as file:
                file.write(fileData)

            connectionSocket.send(f"File '{filename}' received successfully.".encode())
        except Exception as e:
            error_message = f"Error receiving file '{filename}': {e}"
            connectionSocket.send(error_message.encode())

    # GET
    elif command.startswith("get"):
        try:
            # Extract filename
            _, filename = command.split(" ", 1)

            # Check if the file exists
            if not os.path.isfile(filename):
                connectionSocket.send(f"Error: File '{filename}' not found.".encode())
                continue

            # Send the file size first
            fileSize = os.path.getsize(filename)
            connectionSocket.send(str(fileSize).encode())

            # Wait for confirmation from the client
            ack = connectionSocket.recv(4096).decode()
            if ack != "READY":
                print("Client is not ready to receive the file.")
                continue

            # Open the file and send its contnets
            with open(filename, "rb") as file:
                fileData = file.read()
                connectionSocket.send(fileData)
            
            print(f"File '{filename}' sent successfully")
        except Exception as e:
            error_message = f"Error sending file '{filename}': {e}"
            connectionSocket.send(error_message.encode())
    
    # QUIT
    elif command == "quit":
        # Runs quit command and closes connection
        connectionSocket.send("Connection closed.".encode())
        connectionSocket.close()
        print(f"Connection with {clientAddr} closed.")
        continue # Needed to wait for new connections

    else:
        # Wrong command (user error input)
        connectionSocket.send("Unknown commnad".encode())

    # CLOSES CONNECTION
    connectionSocket.close()