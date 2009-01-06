"""
basic class object for storing files
"""
class File(object):

    def __init__(self, file, filename, mimetype):
        self.file = file
        self.filename = filename
        self.mimetype = mimetype

