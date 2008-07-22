import datetime
import unittest

from schemaish import *


class TestString(unittest.TestCase):

    def test_validate(self):
        self.assertEquals(String("String").validate(""), "")
        self.assertEquals(String("String").validate(None), None)
        self.assertRaises(Invalid, String("String", validator=NotEmpty()).validate, None)
        self.assertRaises(Invalid, String("String", validator=NotEmpty()).validate, "")


class TestDate(unittest.TestCase):

    def test_validate(self):
        today = datetime.date.today()
        self.assertEquals(Date("Date").validate(None), None)
        self.assertEquals(Date("Date").validate(today), today)
        self.assertEquals(Date("Date", validator=NotEmpty).validate(today), today)
        self.assertRaises(Invalid, Date("Date", validator=NotEmpty).validate, None)


class TestSequence(unittest.TestCase):

    def test_validate(self):
        s = Sequence("Sequence", attr=String("string", "String"))
        self.assertEquals(s.validate([]), [])
        self.assertEquals(s.validate(["one", "two"]), ["one", "two"])
        s = Sequence("Sequence", attr=String("string", "String"), validator=NotEmpty)
        self.assertEquals(s.validate(["one"]), ["one"])
        self.assertRaises(Invalid, s.validate, [])
        s = Sequence("Sequence", attr=String("string", "String", validator=NotEmpty))
        self.assertEquals(s.validate([]), [])
        self.assertRaises(Invalid, s.validate, [""])


class TestTuple(unittest.TestCase):

    def test_validate(self):
        t = Tuple("Tuple", attrs=[String("One"), String("Two")])
        self.assertEquals(t.validate(tuple()), tuple())
        self.assertEquals(t.validate(("one", "two")), ("one", "two"))
        t = Tuple("Tuple", attrs=[String("One"), String("Two")], validator=NotEmpty)
        self.assertEquals(t.validate(("one",)), ("one",))
        self.assertRaises(Invalid, t.validate, tuple())
        t = Tuple("Tuple", attrs=[String("One", validator=NotEmpty), String("Two")])
        self.assertEquals(t.validate(("one", "two")), ("one", "two"))
        self.assertEquals(t.validate(("one", "")), ("one", ""))
        self.assertRaises(Invalid, t.validate, ("", ""))


class TestStructure(unittest.TestCase):

    def test_validate_empty(self):
        s = Structure("Structure", attrs=[])
        self.assertEquals(s.validate({}), {})
        self.assertEquals(s.validate({"notanattr": "bleurgh!"}), {})

    def test_validate_extra(self):
        s = Structure("Structure", attrs=[("one", String("One"))])
        self.assertEquals(s.validate({"one": "un", "notanattr": "Hah!"}), {"one": "un"})

    def test_validate_attrs(self):
        s = Structure("Structure", attrs=[("one", String("One")), ("two", String("Two"))])
        self.assertEquals(s.validate({"one": "un", "two": "deux"}), {"one": "un", "two": "deux"})
        self.assertRaises(KeyError, s.validate, {})

    def test_validate_nested(self):

        one = Structure("One", attrs=[("a", String("A")), ("b", String("B"))])
        two = Structure("Two", attrs=[("a", String("A")), ("b", String("B"))])
        s = Structure("Structure", attrs=[("one", one), ("two", two)])
        self.assertEquals(s.validate({"one": {"a": "1a", "b": "1b"}, "two": {"a": "2a", "b": "2b"}}), {"one": {"a": "1a", "b": "1b"}, "two": {"a": "2a", "b": "2b"}})

        s = Structure("Structure", attrs=[
            ("one", Structure("One", attrs=[
                ("a", String("A", validator=NotEmpty)),
                ("b", String("B")),
                ])),
            ])
        self.assertEquals(s.validate({"one": {"a": "1a", "b": "1b"}}), {"one": {"a": "1a", "b": "1b"}})
        self.assertRaises(Invalid, s.validate, {"one": {"a": "", "b": "1b"}})
        self.assertRaises(Invalid, s.validate, {"one": {"a": None, "b": "1b"}})

    def test_add(self):
        s = Structure("Structure")
        s.add("one", String("One"))
        s.add("two", String("Two"))
        self.assertEquals(s.validate({"one": "un", "two": "deux"}), {"one": "un", "two": "deux"})

    def test_get(self):
        one = String("One")
        s = Structure("Structure", attrs=[("one", one)])
        self.assertTrue(s.get("one") is one)
        self.assertRaises(KeyError, s.get, "two")

    def test_meta_order(self):

        class Test(Structure):
            c = String("A")
            wibble = String("Wibble")
            b = String("A")
            wobble = String("Wobble")
            plop = String("Pol")
            a = String("A")

        self.assertEquals([a[0] for a in Test.attrs], ["c", "wibble", "b", "wobble", "plop", "a"])

    def test_meta(self):

        class TestStructure(Structure):
            one = String("One", validator=NotEmpty)
            two = String("Two")

        s = TestStructure("Structure")
        self.assertEquals(s.validate({"one": "One", "two": "Two"}), {"one": "One", "two": "Two"})
        self.assertRaises(Invalid, s.validate, {"one": "", "two": "Two"})


if __name__ == "__main__":
    unittest.main()

