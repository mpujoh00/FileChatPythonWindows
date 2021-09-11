import os.path
import sys
from threading import Thread
from pathlib import Path
import socket


class ClientHandler(Thread):
    def __init__(self, socket, database):
        Thread.__init__(self)
        self.sock = socket
        self.connection = socket[0]
        self.address = socket[1]
        self.database = database
        self.currentUser = None
        self.client = ""
        print("Connection established with client: ", self.address)

    def run(self):
        # indicates what server it is
        self.send_message("python")
        # gets what client it is
        try:
            self.client = self.read_message()
        except socket.error:
            # client fail
            print("Client: " + str(self.address) + " unexpectedly disconnected")
            sys.exit()

        # login or registration menu
        print(" - Asking to login or register")
        quitApp = True
        try:
            quitApp = self.show_login_menu()
        except socket.error:
            # client fail
            print("Client: " + str(self.address) + " unexpectedly disconnected")
            sys.exit()

        # main menu
        try:
            self.show_menu(quitApp)
        except socket.error:
            # client fail
            print("Client: " + str(self.address) + " unexpectedly disconnected")
            # disconnects user
            self.database.disconnect_user(self.currentUser.username)

    def show_login_menu(self):
        run = True
        quitApp = False
        while run:
            self.send_message("What do you want to do?\n\ta. Login\n\tb. Register\n\tc.Quit\nChoice:")
            choice = self.read_message()
            if choice == "a":
                # login
                print(" - Requesting login data")
                self.currentUser = self.login()
                if self.currentUser is not None:
                    run = False
            elif choice == "b":
                # registration
                print(" - Registering new user")
                self.currentUser = self.register()
                if self.currentUser is not None:
                    run = False
            elif choice == "c":
                # quit
                print(" - Disconnecting client " + str(self.address) + " from the server")
                self.send_message("Goodbye!")
                run = False
                quitApp = True
            else:
                print(" - Incorrect choice, trying again")
                self.send_message("Incorrect choice, try again\n")
        return quitApp

    def show_menu(self, quitApp):
        while not quitApp:
            print(" - Displaying menu")
            self.send_message(
                "What do you want to do?\n\ta. Check user's state\n\tb. Send file\n\tc. Refresh received files"
                "\n\td. Change file extensions\n\te. Quit\nChoice:")
            choice = self.read_message()
            if choice == "a":
                # checks another user's state
                print(" - Checking user's state")
                self.check_state()
            elif choice == "b":
                # open chat
                print(" - Sending a file")
                self.open_send_file()
            elif choice == "c":
                # checks if there is any new file received
                print(" - Checking for new received files")
                self.received_files()
            elif choice == "d":
                # change extensions
                print(" - Changing accepted file extensions")
                self.change_extensions()
            elif choice == "e":
                # quit app
                print(" - Disconnecting client '" + self.currentUser.username + "' from the server")
                self.send_message("Goodbye!")
                self.database.disconnect_user(self.currentUser.username)
                quitApp = True
            else:
                # incorrect choice
                print(" - Trying to choose a menu option again")
                self.send_message("Incorrect option, try again\n")

    def check_state(self):
        self.send_message("Who do you want to know about? (q)\nUsername:")
        username = self.read_message()
        if username == "q":
            return
        friend = self.database.get_user(username)
        if friend is None:
            print(" - User doesn't exist")
            self.send_message("That user doesn't exist\n")
        elif friend.isAvailable:  # friend is connected
            print(" - User is connected")
            self.send_message("The user is connected\n")
        else:
            print(" - User is disconnected")
            self.send_message("The user is disconnected\n")

    def open_send_file(self):
        while True:
            # ask for friend
            print(" - Asking for username")
            self.send_message("To whom do you want to send the file? (q)\nUsername:")
            friendUsername = self.read_message()
            if friendUsername == "q":
                return
            # check if friend's user exists
            friend = self.database.get_user(friendUsername)
            if friend is None:  # friend doesn't exists
                print(" - Username doesn't exist")
                self.send_message("Username doesn't exist, try again\n")
            elif friendUsername == self.currentUser.username:  # same current user
                print(" - Same user")
                self.send_message("You can't send a file to yourself, try again\n")
            elif not friend.isAvailable:  # friend is disconnected
                print(" - User is disconnected")
                self.send_message("The user is disconnected, can't send message\n")
                return
            else:  # friend is available
                while True:
                    print(" - Choosing file to send")
                    self.send_message("What file do you want to send?")
                    # gets file size
                    print(" - Reading file from client")
                    fileSize = int(self.read_message())
                    if fileSize > 65536:
                        self.send_message("File too big (only allowed up to 64kb), try again\n")
                        continue
                    else:
                        self.send_message("ok")
                    # gets file name
                    filename = self.read_message()
                    # checks if the user chose a file
                    if filename == "q":
                        break
                    filename = filename.split("[")[0]
                    # checks if the file extension is accepted by the other user
                    fileExtension = filename.split(".")[1]
                    acceptedExtensions = friend.extensions.split(",")
                    # invalid file extension
                    if fileExtension not in acceptedExtensions:
                        print(" - File extension not valid")
                        self.send_message("File extension not accepted, only valid: " + friend.extensions +
                                          ". Try again\n")
                    else:  # correct file extension
                        self.send_message("ok")
                        filename = "files/" + filename
                        # reads file
                        if self.client == "java":
                            self.read_file_java(filename, fileSize)
                        else:
                            self.read_file_python(filename, fileSize)
                        # saves file to database
                        print(" - Uploading file to database")
                        self.database.upload_file(friend.id, self.currentUser.id, filename)
                        self.send_message("File correctly sent\n")
                        break
                break

    # reads a file sent over a java socket
    def read_file_java(self, filename, fileSize):
        # creates path if it didn't exist
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        # reads file
        file = open(filename, "wb")
        while fileSize > 0:
            data = self.connection.recv(1024)
            file.write(data)
            fileSize -= len(data)
        file.close()

    # reads a file sent over a python socket
    def read_file_python(self, filename, fileSize):
        # creates path if it didn't exist
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        file = open(filename, "wb")
        readBytes = 0
        while fileSize != readBytes:
            # reception confirmation message
            self.send_message("ok")
            # reads bytes
            line = self.connection.recv(8192)
            # writes to file
            file.write(line)
            # updates amount of read bytes
            readBytes += len(line)
        file.close()

    # checks if there is any new file received
    def received_files(self):
        print(" - Checking if any file has been received")
        files = self.database.get_files(self.currentUser.id)
        if not files:
            print(" - No new files")
            self.send_message("You haven't received any new files\n")
        else:
            print(" - New files received")
            for file in files:
                # sends file to user
                friend = self.database.get_user_by_id(file.fromId)
                self.send_message("You have received a new file from '" + friend.username + "': " + file.filename)
                self.send_file(file.filename)
                # waits for confirmation message
                self.read_message()
                print("- File received by user")
            self.send_message("")
            # removes files from database
            for file in files:
                self.database.delete_file(file.id)

    # sends file to socket
    def send_file(self, filename):
        print(" - Sending new file to user")
        file = open("files/" + filename, "rb")
        # sends file size (bytes)
        fileSize = Path("files/" + filename).stat().st_size
        self.send_message(str(fileSize))
        # sends file data
        line = file.read(8192)
        while line:
            # waits for reception confirmation message
            self.read_message()
            # sends bytes
            self.connection.send(line)
            line = file.read(8192)
        file.close()

    def change_extensions(self):
        currentExtensions = self.currentUser.extensions
        run = True
        while run:
            self.send_message("Your current accepted extensions are: " + currentExtensions +
                              "\nIntroduce the new ones from the list [jpg,png,txt,pdf] (separated by commas) (q):")
            newExtensions = self.read_message()
            if newExtensions == "q":
                return
            # check if it's okay
            availableExtensions = ["jpg", "png", "txt", "pdf"]
            chosenExtensions = newExtensions.split(",")
            incorrect = False
            for extension in chosenExtensions:
                # chosen extensions are not correct
                if extension not in availableExtensions:
                    print(" - Incorrect extensions, trying again")
                    self.send_message("Incorrect extensions, try again\n")
                    incorrect = True
                    break
            if incorrect:
                continue
            # update user
            self.database.update_user_extensions(self.currentUser.username, newExtensions)
            self.currentUser.extensions = newExtensions
            print(" - Correctly changed extensions")
            self.send_message("Extensions changed\n")
            run = False

    def login(self):
        while True:
            self.send_message("Introduce your username (q):")
            username = self.read_message()
            if username == "q":
                return None
            self.send_message("Introduce your password (q):")
            password = self.read_message()
            if password == "q":
                return None
            # check if the data is correct
            user = self.database.get_user(username)
            if user is None:
                self.send_message("The user doesn't exist, try again\n")
                print(" - Trying to login again")
            elif user.password != password:
                self.send_message("Incorrect password, try again\n")
                print(" - Trying to login again")
            elif user.isAvailable:
                self.send_message("That user is already connected, try again\n")
                print(" - Trying to login again")
            else:
                self.send_message("Correct data, logging in...\n")
                print(" - Logging in...")
                user.isAvailable = True
                self.database.connect_user(username)
                return user

    def register(self):
        while True:
            self.send_message("Introduce your new username (q):")
            username = self.read_message()
            if username == "q":
                return None
            self.send_message("Introduce your new password (q):")
            password = self.read_message()
            if password == "q":
                return None
            # checks if the username already exists
            user = self.database.get_user(username)
            if user is None:
                print(" - Creating new user...")
                # registers user in the database
                self.database.register_user(username, password)
                return self.database.get_user(username)
            else:
                self.send_message("That username already exists, try again\n")
                print(" - Trying to register again")

    def send_message(self, message):
        try:
            self.connection.send(bytes(message + "\r\n", "UTF-8"))
        except socket.error:
            pass

    def read_message(self):
        try:
            return self.connection.recv(1024).decode(encoding="UTF-8").rstrip()
        except socket.error:
            raise
