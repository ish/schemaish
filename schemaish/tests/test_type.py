import unittest

class FileTests(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from schemaish.type import File
        return File(*arg, **kw)

    def test_ctor(self):
        f = self._makeOne('file', 'filename', 'mimetype')
        self.assertEqual(f.file, 'file')
        self.assertEqual(f.filename, 'filename')
        self.assertEqual(f.mimetype, 'mimetype')
        self.assertEqual(f.metadata, {})

    def test_repr_with_file(self):
        f = self._makeOne('file', 'filename', 'mimetype')
        result = repr(f)
        self.failUnless(result.startswith(
            """<schemaish.type.File file="\'file\'" filename=\"filename\""""))
        self.failUnless(result.endswith(
            """mimetype="mimetype", metadata="{}" >"""))
        
        
