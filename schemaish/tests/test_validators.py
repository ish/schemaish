import unittest
import schemaish


class TestValidators(unittest.TestCase):

    def test_always(self):
        v = schemaish.Always()
        v.to_python('foo')
        v.to_python('')
        v.to_python(1)
        v.to_python([1,2,3])
        v.to_python(None)


if __name__ == '__main__':
    unittest.main()

