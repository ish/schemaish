from formencode.validators import *


class Field(object):

    def __init__(self, name, title, description=None, validator=None):
        self.name = name
        self.title = title
        self.description = description
        self.validator = validator

    def validate(self, value):
        if self.validator is None:
            return value
        return self.validator.to_python(value)


class String(Field):
    pass


class Integer(Field):
    pass


class Float(Field):
    pass


class Decimal(Field):
    pass


class Date(Field):
    pass


class Time(Field):
    pass


class DateTime(Field):
    pass


class Sequence(Field):

    def __init__(self, *a, **k):
        field = k.pop("field")
        super(Sequence, self).__init__(*a, **k)
        self.field = field

    def validate(self, value):
        value = [self.field.validate(item) for item in value]
        return super(Sequence, self).validate(value)


class Tuple(Field):

    def __init__(self, *a, **k):
        fields = k.pop("fields")
        super(Tuple, self).__init__(*a, **k)
        self.fields = fields

    def validate(self, value):
        value = tuple(field.validate(item) for (field, item) in zip(self.fields, value))
        return super(Tuple, self).validate(value)


class Structure(Field):

    def __init__(self, *a, **k):
        fields = k.pop('fields')
        super(Structure, self).__init__(*a, **k)
        self.fields = fields

    def validate(self, value):
        value = dict((field.name, field.validate(value[field.name])) for field in self.fields)
        return super(Structure, self).validate(value)


if __name__ == "__main__":

    import datetime
    import unittest

    class TestString(unittest.TestCase):

        def test_validate(self):
            self.assertEquals(String("string", "String").validate(""), "")
            self.assertEquals(String("string", "String").validate(None), None)
            self.assertRaises(Invalid, String("string", "String", validator=NotEmpty()).validate, None)
            self.assertRaises(Invalid, String("string", "String", validator=NotEmpty()).validate, "")

    class TestDate(unittest.TestCase):

        def test_validate(self):
            today = datetime.date.today()
            self.assertEquals(Date("date", "Date").validate(None), None)
            self.assertEquals(Date("date", "Date").validate(today), today)
            self.assertEquals(Date("date", "Date", validator=NotEmpty).validate(today), today)
            self.assertRaises(Invalid, Date("date", "Date", validator=NotEmpty).validate, None)

    class TestSequence(unittest.TestCase):

        def test_validate(self):
            s = Sequence("sequence", "Sequence", field=String("string", "String"))
            self.assertEquals(s.validate([]), [])
            self.assertEquals(s.validate(["one", "two"]), ["one", "two"])
            s = Sequence("sequence", "Sequence", field=String("string", "String"), validator=NotEmpty)
            self.assertEquals(s.validate(["one"]), ["one"])
            self.assertRaises(Invalid, s.validate, [])
            s = Sequence("sequence", "Sequence", field=String("string", "String", validator=NotEmpty))
            self.assertEquals(s.validate([]), [])
            self.assertRaises(Invalid, s.validate, [""])

    class TestTuple(unittest.TestCase):

        def test_validate(self):
            t = Tuple("tuple", "Tuple", fields=[String("one", "One"), String("two", "Two")])
            self.assertEquals(t.validate(tuple()), tuple())
            self.assertEquals(t.validate(("one", "two")), ("one", "two"))
            t = Tuple("tuple", "Tuple", fields=[String("one", "One"), String("two", "Two")], validator=NotEmpty)
            self.assertEquals(t.validate(("one",)), ("one",))
            self.assertRaises(Invalid, t.validate, tuple())
            t = Tuple("tuple", "Tuple", fields=[String("one", "One", validator=NotEmpty), String("two", "Two")])
            self.assertEquals(t.validate(("one", "two")), ("one", "two"))
            self.assertEquals(t.validate(("one", "")), ("one", ""))
            self.assertRaises(Invalid, t.validate, ("", ""))

    class TestStructure(unittest.TestCase):

        def test_validate_empty(self):
            s = Structure("structure", "Structure", fields=[])
            self.assertEquals(s.validate({}), {})
            self.assertEquals(s.validate({"notafield": "bleurgh!"}), {})

        def test_validate_extra(self):
            s = Structure("structure", "Structure", fields=[String("one", "One")])
            self.assertEquals(s.validate({"one": "un", "notafield": "Hah!"}), {"one": "un"})

        def test_validate_fields(self):
            s = Structure("structure", "Structure", fields=[String("one", "One"), String("two", "Two")])
            self.assertEquals(s.validate({"one": "un", "two": "deux"}), {"one": "un", "two": "deux"})
            self.assertRaises(KeyError, s.validate, {})

        def test_validate_nested(self):

            one = Structure("one", "Structure", fields=[String("a", "A"), String("b", "B")])
            two = Structure("two", "Structure", fields=[String("a", "A"), String("b", "B")])
            s = Structure("structure", "Structure", fields=[one, two])
            self.assertEquals(s.validate({"one": {"a": "1a", "b": "1b"}, "two": {"a": "2a", "b": "2b"}}), {"one": {"a": "1a", "b": "1b"}, "two": {"a": "2a", "b": "2b"}})

            s = Structure("structure", "Structure", fields=[
                Structure("one", "Structure", fields=[String("a", "A", validator=NotEmpty), String("b", "B")]),
                ])
            self.assertEquals(s.validate({"one": {"a": "1a", "b": "1b"}}), {"one": {"a": "1a", "b": "1b"}})
            self.assertRaises(Invalid, s.validate, {"one": {"a": "", "b": "1b"}})
            self.assertRaises(Invalid, s.validate, {"one": {"a": None, "b": "1b"}})

    unittest.main()

