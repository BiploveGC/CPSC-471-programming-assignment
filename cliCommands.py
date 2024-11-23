import os
import socket
import sys


# Command line check
if len(sys.argv) < 3:
    print("COMMAND: python cli.py <SERVER_MACHINE> <PORT_NUMBER>")
    sys.exit()


# Server address and port (from command line)
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

# Create a TCP socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
clientSocket.connect((serverName, serverPort))

# Get command from command line (user)
command = input("Enter command (ls, put <filename>, get <filename>, quit): ")

# Send command to the server
clientSocket.send(command.encode())

#COMMANDS -------------------------------

# GET command (client side)
if command.startswith("get"):
    # Extract filename from the command
    _, filename = command.split(" ", 1)

    # Receive the file size from the server
    fileSize = clientSocket.recv(4096).decode()

    # If the server sent an error message instead of file size
    if fileSize.startswith("Error"):
        print(f"Server response: {fileSize}")
    else:
        # Confirm to the server that the client is ready to receive the file
        clientSocket.send("READY".encode())

        # Receive the file data
        fileData = clientSocket.recv(int(fileSize))

        # Write the received data to a new file
        with open(filename, "wb") as file:
            file.write(fileData)

        print(f"File '{filename}' received successfully.")


# PUT command (client side)
elif command.startswith("put"):
    _, filename = command.split(" ", 1)

    # Check if file exists
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' does not exist")
        clientSocket.close()
        sys.exit()

    # Open the file & read its content
    with open(filename, "rb") as file:
        fileData = file.read()    

    # Send file size first
    fileSize = len(fileData)
    clientSocket.send(str(fileSize).encode())

    # Send file data
    clientSocket.send(fileData)

    # Receive and print resposne from the server
    response = clientSocket.recv(4096).decode()
    print(f"Server response:\n{response}")

# Close Socket
clientSocket.close()