
class User:
    def __init__(self, userId, username, password, extensions, isAvailable):
        self.id = userId
        self.username = username
        self.password = password
        self.extensions = extensions
        self.isAvailable = isAvailable
