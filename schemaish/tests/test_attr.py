import datetime
import unittest

from schemaish import *


class TestCore(unittest.TestCase):

    def test_blank(self):
        a = String()
        self.assertTrue(a.title is None)
        self.assertTrue(a.description is None)
        self.assertTrue(a.validator is None)

    def test_positional(self):
        self.assertRaises(TypeError, String, "a")

    def test_title(self):
        self.assertEquals(String(title="Title").title, "Title")

    def test_description(self):
        self.assertEquals(String(description="Description").description, "Description")

    def test_meta_order(self):
        a = String()
        b = String()
        self.assertTrue(a._meta_order < b._meta_order)


class TestString(unittest.TestCase):

    def test_validate(self):
        String().validate("")
        String().validate(None)
        self.assertRaises(Invalid, String(validator=NotEmpty()).validate, None)
        self.assertRaises(Invalid, String(validator=NotEmpty()).validate, "")


class TestDate(unittest.TestCase):

    def test_validate(self):
        today = datetime.date.today()
        Date().validate(None)
        Date().validate(today)
        Date(validator=NotEmpty).validate(today)
        self.assertRaises(Invalid, Date(validator=NotEmpty).validate, None)


class TestSequence(unittest.TestCase):

    def test_validate(self):
        s = Sequence(String())
        s.validate(None)
        s.validate([])
        s.validate(["one", "two"])
        s = Sequence(attr=String(), validator=NotEmpty)
        s.validate(["one"])
        self.assertRaises(Invalid, s.validate, [])
        s = Sequence(String(validator=NotEmpty))
        s.validate([])
        self.assertRaises(Invalid, s.validate, [""])


class TestTuple(unittest.TestCase):

    def test_validate(self):
        t = Tuple([String(), String()])
        t.validate(None)
        t.validate(tuple())
        t.validate(("one", "two"))
        t = Tuple([String(), String()], validator=NotEmpty)
        t.validate(("one",))
        self.assertRaises(Invalid, t.validate, tuple())
        t = Tuple([String(validator=NotEmpty), String()])
        t.validate(("one", "two"))
        t.validate(("one", ""))
        self.assertRaises(Invalid, t.validate, ("", ""))


class TestStructure(unittest.TestCase):

    def test_validate_empty(self):
        s = Structure([])
        s.validate({})
        s.validate({"notanattr": "bleurgh!"})

    def test_validate_extra(self):
        s = Structure([("one", String())])
        s.validate({"one": "un", "notanattr": "Hah!"})

    def test_validate_attrs(self):
        s = Structure([("one", String()), ("two", String())])
        s.validate({"one": "un", "two": "deux"})
        self.assertRaises(KeyError, s.validate, {})

    def test_validate_nested(self):

        one = Structure([("a", String()), ("b", String())])
        two = Structure([("a", String()), ("b", String())])
        s = Structure([("one", one), ("two", two)])
        s.validate({"one": {"a": "1a", "b": "1b"}, "two": {"a": "2a", "b": "2b"}})

        s = Structure([
            ("one", Structure([
                ("a", String(validator=NotEmpty)),
                ("b", String()),
                ])),
            ])
        s.validate({"one": {"a": "1a", "b": "1b"}})
        self.assertRaises(Invalid, s.validate, {"one": {"a": "", "b": "1b"}})
        self.assertRaises(Invalid, s.validate, {"one": {"a": None, "b": "1b"}})

    def test_add(self):
        s = Structure()
        s.add("one", String())
        s.add("two", String())
        s.validate({"one": "un", "two": "deux"})

    def test_get(self):
        one = String()
        s = Structure([("one", one)])
        self.assertTrue(s.get("one") is one)
        self.assertRaises(KeyError, s.get, "two")

    def test_meta_order(self):

        class Test(Structure):
            c = String()
            wibble = String()
            b = String()
            wobble = String()
            plop = String()
            a = String()

        self.assertEquals([a[0] for a in Test.attrs], ["c", "wibble", "b", "wobble", "plop", "a"])

    def test_meta(self):

        class TestStructure(Structure):
            one = String(validator=NotEmpty)
            two = String()

        s = TestStructure()
        s.validate({"one": "One", "two": "Two"})
        self.assertRaises(Invalid, s.validate, {"one": "", "two": "Two"})

    def test_extend_meta(self):

        class TestStructure(Structure):
            one = String(validator=NotEmpty)
            two = String()

        s1 = TestStructure()
        s2 = TestStructure()
        self.assertEquals(len(s1.attrs), 2)
        self.assertEquals(len(s2.attrs), 2)

        s2.add('three', String())
        self.assertEquals(len(s1.attrs), 2)
        self.assertEquals(len(s2.attrs), 3)

        
class TestRecursiveValidate(unittest.TestCase):

    def test_validate_sequence(self):
        s = Sequence(String(validator=NotEmpty))
        try:
            s.validate( ["",""] )
        except Invalid, e:
            print e.error_dict
            
    def test_validate_structure(self):
        s = Structure([('list',Sequence(String(validator=NotEmpty)))])
        try:
            s.validate( {'list':["",""]} )
        except Invalid, e:
            print e.error_dict


if __name__ == "__main__":
    unittest.main()

