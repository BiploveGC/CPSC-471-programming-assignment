import os
import socket
import sys

# Command line check
if len(sys.argv) < 2:
    print("COMMAND: python3 serv.py <PORT_NUMBER>")
    sys.exit()

# Get the port number from the command line
serverPort = int(sys.argv[1])

# Create TCP socket for control channel
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to a port
serverSocket.bind(('', serverPort))

# Start listening on socket
serverSocket.listen(1)
print(f"Server is listening on port {serverPort}...")

# Accept connections forever (receive data from client)
while True:
    # Accept a new connection
    connectionSocket, clientAddr = serverSocket.accept()
    print(f"Accepted connection from {clientAddr}")

    # Continuously handle commands from the same connection
    while True:
        try:
            # Receive the command from the client
            command = connectionSocket.recv(4096).decode().strip()

            # If no command received, close the connection
            if not command:
                print(f"Connection with {clientAddr} closed unexpectedly due to no command received.")
                break

            print(f"Received command: {command}")

            # Handle 'ls' Command
            if command == "ls":
                try:
                    # Run 'ls' command using os.listdir() to list files
                    files = os.listdir('.')
                    result = "\n".join(files)
                    connectionSocket.send(result.encode())
                except Exception as e:
                    error_message = f"Error executing ls command: {e}"
                    connectionSocket.send(error_message.encode())

            # Handle 'put' Command
            elif command.startswith("put"):
                try:
                    # Extract filename
                    _, filename = command.split(" ", 1)

                    # Receive the ephemeral port number from the client
                    dataPortStr = connectionSocket.recv(4096).decode().strip()
                    print(f"Received ephemeral port for data channel: {dataPortStr}")

                    # Ensure that the received port is a valid integer
                    dataPort = int(dataPortStr)

                    # Create a new socket for the data channel
                    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    dataSocket.connect((clientAddr[0], dataPort))

                    # Receive the size of the file
                    fileSizeStr = dataSocket.recv(4096).decode().strip()
                    print(f"Received file size: {fileSizeStr}")

                    # Ensure that the fileSize is a valid integer
                    fileSize = int(fileSizeStr)

                    # Receive the actual file data in chunks
                    fileData = b""
                    remaining = fileSize
                    while remaining > 0:
                        chunk = dataSocket.recv(min(4096, remaining))
                        if not chunk:
                            raise Exception("Connection lost while receiving file data.")
                        fileData += chunk
                        remaining -= len(chunk)

                    # Save the received data to a new file
                    with open(filename, "wb") as file:
                        file.write(fileData)

                    dataSocket.close()
                    connectionSocket.send(f"File '{filename}' received successfully.".encode())
                except Exception as e:
                    error_message = f"Error receiving file '{filename}': {e}"
                    print(error_message)  # Log the error for debugging
                    connectionSocket.send(error_message.encode())

            # Handle 'get' Command
            elif command.startswith("get"):
                try:
                    # Extract filename
                    _, filename = command.split(" ", 1)

                    # Check if the file exists
                    if not os.path.isfile(filename):
                        connectionSocket.send(f"Error: File '{filename}' not found.".encode())
                        continue

                    # Receive the ephemeral port number from the client
                    dataPortStr = connectionSocket.recv(4096).decode().strip()
                    print(f"Received ephemeral port for data channel: {dataPortStr}")

                    # Ensure that the received port is a valid integer
                    dataPort = int(dataPortStr)

                    # Create a new socket for the data channel
                    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    dataSocket.connect((clientAddr[0], dataPort))

                    # Send the file size first
                    fileSize = os.path.getsize(filename)
                    dataSocket.send(str(fileSize).encode())

                    # Wait for confirmation from the client
                    ack = dataSocket.recv(4096).decode().strip()
                    if ack != "READY":
                        print("Client is not ready to receive the file.")
                        dataSocket.close()
                        continue

                    # Open the file and send its contents
                    with open(filename, "rb") as file:
                        while True:
                            chunk = file.read(4096)
                            if not chunk:
                                break
                            dataSocket.send(chunk)

                    dataSocket.close()
                    print(f"File '{filename}' sent successfully.")
                except Exception as e:
                    error_message = f"Error sending file '{filename}': {e}"
                    print(error_message)  # Log the error for debugging
                    connectionSocket.send(error_message.encode())

            # Handle 'quit' Command
            elif command == "quit":
                # Send quit message and close connection
                connectionSocket.send("Connection closed.".encode())
                connectionSocket.close()
                print(f"Connection with {clientAddr} closed.")
                break  # Exit the loop to accept new connections

            # Handle Unknown Command
            else:
                connectionSocket.send("Unknown command.".encode())

        except Exception as e:
            print(f"Exception occurred: {e}")
            break

    # Close the connection after quit or unexpected disconnect
    connectionSocket.close()
