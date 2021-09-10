import os
import os.path
import errno

class File:
    def __init__(self, fileId, toId, fromId, fileData, filename):
        self.id = fileId
        self.toId = toId
        self.fromId = fromId
        self.filename = filename
        # creates path if it didn't exist
        if not os.path.exists(os.path.dirname("files/" + filename)):
            try:
                os.makedirs(os.path.dirname("files/" + filename))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        # writes file
        self.file = open("files/" + filename, "wb")
        self.file.write(fileData)
        self.file.close()
