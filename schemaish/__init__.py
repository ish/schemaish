from formencode.validators import *


class Attribute(object):

    def __init__(self, title, description=None, validator=None):
        self.title = title
        self.description = description
        self.validator = validator

    def validate(self, value):
        if self.validator is None:
            return value
        return self.validator.to_python(value)


class String(Attribute):
    pass


class Integer(Attribute):
    pass


class Float(Attribute):
    pass


class Decimal(Attribute):
    pass


class Date(Attribute):
    pass


class Time(Attribute):
    pass


class DateTime(Attribute):
    pass


class Sequence(Attribute):

    def __init__(self, *a, **k):
        attr = k.pop("attr")
        super(Sequence, self).__init__(*a, **k)
        self.attr = attr

    def validate(self, value):
        value = [self.attr.validate(item) for item in value]
        return super(Sequence, self).validate(value)


class Tuple(Attribute):

    def __init__(self, *a, **k):
        attrs = k.pop("attrs")
        super(Tuple, self).__init__(*a, **k)
        self.attrs = attrs

    def validate(self, value):
        value = tuple(attr.validate(item) for (attr, item) in zip(self.attrs, value))
        return super(Tuple, self).validate(value)


class _StructureMeta(type):

    def __new__(cls, name, bases, clsattrs):
        attrs = []
        for (name, value) in clsattrs.items():
            if isinstance(value, Attribute):
                attrs.append((name, value))
                del clsattrs[name]
        clsattrs["attrs"] = attrs
        return type.__new__(cls, name, bases, clsattrs)


class Structure(Attribute):

    __metaclass__ = _StructureMeta

    attrs = []

    def __init__(self, *a, **k):
        attrs = k.pop('attrs', None)
        super(Structure, self).__init__(*a, **k)
        if attrs is not None:
            self.attrs = attrs

    def add(self, name, attr):
        self.attrs.append((name, attr))

    def get(self, name):
        for (attr_name, attr) in self.attrs:
            if attr_name == name:
                return attr
        raise KeyError(name)

    def validate(self, value):
        value = dict((name, attr.validate(value[name])) for (name, attr) in self.attrs)
        return super(Structure, self).validate(value)


if __name__ == "__main__":

    import datetime
    import unittest

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

        def test_meta(self):

            class TestStructure(Structure):
                one = String("One", validator=NotEmpty)
                two = String("Two")

            s = TestStructure("Structure")
            self.assertEquals(s.validate({"one": "One", "two": "Two"}), {"one": "One", "two": "Two"})
            self.assertRaises(Invalid, s.validate, {"one": "", "two": "Two"})

    unittest.main()

