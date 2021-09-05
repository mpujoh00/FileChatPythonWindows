class File:
    def __init__(self, fileId, toId, fromId, fileData, filename):
        self.id = fileId
        self.toId = toId
        self.fromId = fromId
        self.filename = filename
        # writes file
        self.file = open("files/" + filename, "wb")
        self.file.write(fileData)
        self.file.close()
