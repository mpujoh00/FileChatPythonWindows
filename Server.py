from ClientHandler import ClientHandler

from Database import Database
import socket
import threading
import time

global stopDatabase

class Server:
    def __init__(self):
        # database
        self.database = Database()
        # keeps it alive
        global stopDatabase
        stopDatabase = False
        self.databaseThread = threading.Thread(target=self.keep_database_alive)
        self.databaseThread.start()
        # creates server socket
        self.HOST = '127.0.0.1'
        self.PORT = 2021
        self.socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
        # creation of the socket
        self.socketServer.bind((self.HOST, self.PORT))
        # listening for clients
        self.socketServer.listen(5)
        print("Python server listening on ip: " + self.HOST + " port: " + str(self.PORT))

        while True:
            # accepts connection with a client and creates a thread for it
            ClientHandler(self.socketServer.accept(), self.database).start()

    def keep_database_alive(self):
        global stopDatabase
        while not stopDatabase:
            time.sleep(90)
            self.database.keep_alive()

    def stop_server(self):
        global stopDatabase
        stopDatabase = True
        self.socketServer.close()
