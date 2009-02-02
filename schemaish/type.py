"""
basic class object for storing files
"""
class File(object):

    def __init__(self, file, filename, mimetype):
        self.file = file
        self.filename = filename
        self.mimetype = mimetype

    def __repr__(self):
        return '<schemaish.type.File file="%r" filename="%s", mimtype="%s">'%(self.file, self.filename, self.mimetype)

