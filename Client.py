import socket
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
from pathlib import Path

HOST = '127.0.0.1'
PORT = 2021

def send_message(message):
    socket.send(bytes(message + "\r\n", "UTF-8"))

def read_message():
    return socket.recv(1024).decode(encoding="UTF-8")

# connects with the server
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
print("Python client connecting to Java server of ip: " + str(HOST) + " port: " + str(PORT))

print("Waiting for messages")
run = True
# reads messages from the server
while run:
    receivedMessage = read_message()
    if receivedMessage == "What file do you want to send?":
        # sends file to a friend
        print(" - " + receivedMessage)
        # chooses file to send
        Tk().withdraw()
        desktop = os.path.expanduser("~/Desktop")
        filepath = askopenfilename(initialdir=desktop)
        # checks if user canceled operation
        if not filepath:
            send_message("q")
        # file chosen
        else:
            print(filepath)
            # sends file size
            file = open(filepath, "rb")
            fileSize = Path(filepath).stat().st_size
            print(fileSize)
            send_message(str(fileSize))
            # waits to know if the file size is allowed
            validSize = read_message()
            # file size allowed
            if validSize == "ok":
                # sends filename
                filepath = filepath.split("/")
                filename = filepath[len(filepath) - 1]
                send_message(filename)
                # waits to know if the file extension is allowed
                validExtension = read_message()
                if validExtension == "ok":
                    # gets file data
                    line = file.read(8192)
                    while line:
                        # waits for reception confirmation message
                        read_message()
                        # sends bytes
                        socket.send(line)
                        line = file.read(8192)
                    file.close()
                    # waits for confirmation message
                    read_message()
                    print("- File received by user")
                else:
                    print(" - " + validExtension)
            else:
                print(" - " + validSize)

    elif receivedMessage == "You have received a new file from":
        print(" - " + receivedMessage)
        # gets file name
        filename = read_message()
        # creates file
        file = open("/received files/" + filename, "wb")
        # gets file size
        size = read_message()
        # writes file
        while size > 0:
            data = socket.recv(1024)
            file.write(data)
            size -= len(data)
        file.close()

    elif receivedMessage == "Goodbye!":
        print(" - " + receivedMessage)
        run = False
    else:
        print(" - " + receivedMessage)

    # expects an answer
    if receivedMessage.endswith(":"):
        send_message(input())


socket.close()
