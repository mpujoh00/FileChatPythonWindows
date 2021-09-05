import mysql
import mysql.connector as connector
from mysql.connector import errorcode

from File import File
from User import User


class Database:
    def __init__(self):
        try:
            self.connection = connector.connect(user='dq2fDwEP6r', password='eCSdwdyUFv', host='www.remotemysql.com',
                                                database='dq2fDwEP6r')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            print("Successfully connected to the database")

    def register_user(self, username, password):
        cursor = self.connection.cursor()
        query = "INSERT INTO Users (username, password, accepted_extensions, is_available) VALUES (%s,%s,%s,%s)"
        cursor.execute(query, (username, password, "jpg,png,txt,pdf", 1))
        self.connection.commit()
        cursor.close()

    def update_user_extensions(self, username, extensions):
        cursor = self.connection.cursor()
        query = "UPDATE Users SET accepted_extensions=%s WHERE username=%s"
        cursor.execute(query, (extensions, username))
        self.connection.commit()
        cursor.close()

    def connect_user(self, username):
        cursor = self.connection.cursor()
        query = "UPDATE Users SET is_available=%s WHERE username=%s"
        cursor.execute(query, (1, username))
        self.connection.commit()
        cursor.close()

    def disconnect_user(self, username):
        cursor = self.connection.cursor()
        query = "UPDATE Users SET is_available=%s WHERE username=%s"
        cursor.execute(query, (0, username))
        self.connection.commit()
        cursor.close()

    def get_user(self, username):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Users WHERE username=%s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        # user exists
        if user is not None:
            print(user)
            return User(user[0], user[1], user[2], user[3], user[4])
        # user doesn't exist
        else:
            return None

    def get_user_by_id(self, userId):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Users WHERE id=%s"
        cursor.execute(query, (userId,))
        user = cursor.fetchone()
        cursor.close()
        return User(user[0], user[1], user[2], user[3], user[4])

    def upload_file(self, toId, fromId, filename):
        cursor = self.connection.cursor()
        query = "INSERT INTO Files (to_id, from_id, file, file_name) VALUES (%s,%s,%s,%s)"
        file = open(filename, "rb")
        filename = filename.split("/")[1]
        cursor.execute(query, (toId, fromId, file.read(), filename))
        self.connection.commit()
        cursor.close()

    def delete_file(self, id):
        cursor = self.connection.cursor()
        query = "DELETE FROM Files WHERE id=%s"
        cursor.execute(query, (id,))
        self.connection.commit()
        cursor.close()

    def get_files(self, toUserId):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Files WHERE to_id=%s"
        cursor.execute(query, (toUserId,))
        filesData = cursor.fetchall()
        files = []
        for file in filesData:
            files.append(File(file[0], file[1], file[2], file[3], file[4]))
        cursor.close()
        return files

    def keep_alive(self):
        cursor = self.connection.cursor(buffered=True)
        query = "SELECT 1 AS keep_alive"
        cursor.execute(query)
        cursor.close()

    def close_connection(self):
        self.connection.close()
        print("Disconnected from the database")
