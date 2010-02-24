"""
basic class object for storing files
"""
class File(object):
    def __init__(self, file, filename, mimetype, metadata=None):
        self.file = file
        self.filename = filename
        self.mimetype = mimetype
        if metadata is None:
            metadata = {}
        self.metadata = metadata

    def __repr__(self):
        return ('<schemaish.type.File file="%r" filename="%s", '
                'mimetype="%s", metadata="%r" >' % (
                    self.file, self.filename, self.mimetype, self.metadata))

