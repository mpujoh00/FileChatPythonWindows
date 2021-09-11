import socket
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os.path
from pathlib import Path
import errno

JAVA_HOST = '127.0.0.1'
JAVA_PORT = 2021
PYTHON_HOST = '127.0.0.1'
PYTHON_PORT = 2022


def send_message(message):
    try:
        sock.send(bytes(message + "\r\n", "UTF-8"))
    except socket.error:
        pass


def read_message():
    try:
        return sock.recv(1024).decode(encoding="UTF-8").rstrip()
    except socket.error:
        raise


def read_file_python(f, fSize):
    readBytes = 0
    while fSize != readBytes:
        # reception confirmation message
        send_message("ok")
        # reads bytes
        data = sock.recv(8192)
        # writes to file
        f.write(data)
        # updates amount of read bytes
        readBytes += len(data)
    f.close()

def read_file_java(f, fSize):
    # sends confirmation message
    send_message("ok")
    while fSize > 0:
        data = sock.recv(1024)
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
        sock.send(data)
        data = f.read(8192)
    # waits for confirmation message
    read_message()

def connect_to_server(host, port):
    print("Python client connecting to server of ip: " + str(host) + " port: " + str(port))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return s
    except socket.error:
        print("Couldn't connect to the server")
        raise

# connects with the server
try:
    sock = connect_to_server(JAVA_HOST, JAVA_PORT)
except socket.error:
    try:
        sock = connect_to_server(PYTHON_HOST, PYTHON_PORT)
    except socket.error:
        sys.exit()

# gets what server it is
server = read_message()
# indicates what client it is
send_message("python")

print("Waiting for messages")
run = True
# reads messages from the server
while run:
    try:
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
                            sock.send(line)
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
            size = int(sock.recv(1024))
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

    except socket.error:
        # tries to connect to other server
        print("Server failed, trying with another")
        try:
            if server == "java":
                print("Connecting to Python server")
                sock = connect_to_server(PYTHON_HOST, PYTHON_PORT)
            else:
                print("Connecting to Java server")
                sock = connect_to_server(JAVA_HOST, JAVA_PORT)
            server = read_message()
            send_message("python")
        except socket.error:
            # ends program
            print("There isn't any available server")
            run = False

sock.close()
