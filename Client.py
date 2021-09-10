import socket
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os.path
from pathlib import Path
import errno

HOST = '127.0.0.1'
PORT = 2021


def send_message(message):
    socket.send(bytes(message + "\r\n", "UTF-8"))


def read_message():
    return socket.recv(1024).decode(encoding="UTF-8").rstrip()


def read_file_python(f, fSize):
    readBytes = 0
    while fSize != readBytes:
        # reception confirmation message
        send_message("ok")
        # reads bytes
        data = socket.recv(8192)
        # writes to file
        f.write(data)
        # updates amount of read bytes
        readBytes += len(data)
    f.close()

def read_file_java(f, fSize):
    # sends confirmation message
    send_message("ok")
    while fSize > 0:
        data = socket.recv(1024)
        file.write(data)
        fSize -= len(data)
    f.close()

def send_file_java(f):
    # gets file data
    data = f.read(8192)
    while data:
        # waits for reception confirmation message
        read_message()
        # sends bytes
        socket.send(data)
        data = f.read(8192)
    # waits for confirmation message
    read_message()


# connects with the server
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
print("Python client connecting to server of ip: " + str(HOST) + " port: " + str(PORT))

# gets what server it is
server = read_message()
# indicates what client it is
send_message("python")

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
            # sends file size
            file = open(filepath, "rb")
            fileSize = Path(filepath).stat().st_size
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
                    print("- File received by user")
                else:
                    print(" - " + validExtension)
            else:
                print(" - " + validSize)

    elif receivedMessage.startswith("You have received a new file from"):
        print(" - " + receivedMessage)
        # gets file name
        filename = "received files/" + receivedMessage.split(": ")[1]
        # creates path if it didn't exist
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        # creates file
        file = open(filename, "wb")
        # gets file size
        size = int(socket.recv(1024))
        # writes file
        if server == "python":
            read_file_python(file, size)
        else:
            read_file_java(file, size)
        # sends confirmation message
        send_message("ok")

    elif receivedMessage == "Goodbye!":
        print(" - " + receivedMessage)
        run = False
    elif receivedMessage == "":
        print("")
    else:
        print(" - " + receivedMessage)

    # expects an answer
    if receivedMessage.endswith(":"):
        send_message(input())

socket.close()
