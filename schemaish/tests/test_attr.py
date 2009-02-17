import datetime
import unittest

from schemaish import *
from schemaish.attr import Attribute, Invalid

import validatish


class TestCore(unittest.TestCase):

    def test_defaults(self):
        attr = Attribute()
        assert not attr.title
        assert not attr.description
        assert not attr.description
        assert not attr.validator
        assert isinstance(attr.validator, validatish.Always)

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

    def test_subclass(self):
        class Something(Attribute):
            title = 'Title'
            description = 'Description'
            validator = staticmethod(validatish.Required())
        attr = Something()
        assert attr.title is Something.title
        assert attr.description is Something.description
        assert attr.validator is Something.validator
        attr = Something(title=None, description=None, validator=None)
        assert attr.title is None
        assert attr.description is None
        assert attr.validator is None


class TestString(unittest.TestCase):

    def test_validate(self):
        String().validate("")
        String().validate(None)
        self.assertRaises(Invalid, String(validator=validatish.Required()).validate, None)
        self.assertRaises(Invalid, String(validator=validatish.Required()).validate, "")


class TestDate(unittest.TestCase):

    def test_validate(self):
        today = datetime.date.today()
        Date().validate(None)
        Date().validate(today)
        Date(validator=validatish.Required()).validate(today)
        self.assertRaises(Invalid, Date(validator=validatish.Required()).validate, None)


class TestSequence(unittest.TestCase):

    def test_validate(self):
        s = Sequence(String())
        s.validate(None)
        s.validate([])
        s.validate(["one", "two"])
        s = Sequence(attr=String(), validator=validatish.Required())
        s.validate(["one"])
        self.assertRaises(Invalid, s.validate, [])

    def test_nested_validation(self):
        s = Sequence(String(validator=validatish.Required()))
        s.validate([])
        self.assertRaises(Invalid, s.validate, [""])
        s = Sequence(attr=String(validator=validatish.Required()))
        s.validate(['one'])
        self.assertRaises(Invalid, s.validate, [''])
        s = Sequence(Structure([('str', String(validator=validatish.Required()))]))
        s.validate([{'str': 'one'}])
        self.assertRaises(Invalid, s.validate, [{}])

    def test_subclass(self):
        class StringSequence(Sequence):
            attr = String()
        class DateSequence(Sequence):
            attr = Date()
        assert isinstance(StringSequence().attr, String)
        assert isinstance(DateSequence().attr, Date)

    def test_item_error(self):
        """
        Check sequence re-raise exceptions with correct names.
        """
        def fail(value):
            raise validatish.Invalid('fail')
        s = Sequence(String(validator=fail))
        try:
            s.validate([''])
            self.fail()
        except Invalid, e:
            self.assertTrue('0' in e.error_dict)


class TestTuple(unittest.TestCase):

    def test_validate(self):
        t = Tuple([String(), String()])
        t.validate(None)
        t.validate(tuple())
        t.validate(("one", "two"))
        t = Tuple([String(), String()], validator=validatish.Required())
        t.validate(("one", "two"))
        self.assertRaises(Invalid, t.validate, tuple())
        t = Tuple([String(validator=validatish.Required()), String()])
        t.validate(("one", "two"))
        t.validate(("one", ""))
        self.assertRaises(Invalid, t.validate, ("", ""))

    def test_num_items(self):
        self.assertRaises(Invalid, Tuple([String(), String()]).validate, ("one",))

    def test_subclass(self):
        class Tuple1(Tuple):
            attrs = [String(), String(), String()]
        class Tuple2(Tuple):
            attrs = [String(), Date()]
        t1 = Tuple1()
        assert len(t1.attrs) == 3
        assert isinstance(t1.attrs[0], String)
        assert isinstance(t1.attrs[1], String)
        assert isinstance(t1.attrs[2], String)
        t2 = Tuple2()
        assert len(t2.attrs) == 2
        assert isinstance(t2.attrs[0], String)
        assert isinstance(t2.attrs[1], Date)


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

    def test_validate_missing_attrs(self):
        """
        Check that completely missing data validates as long as nothing is required.
        """
        s = Structure([("one", String()), ("two", String())])
        s.validate({})
        s = Structure([("one", String(validator=validatish.Required())), ("two", String())])
        self.assertRaises(Invalid, s.validate, {})

    def test_validate_nested(self):

        one = Structure([("a", String()), ("b", String())])
        two = Structure([("a", String()), ("b", String())])
        s = Structure([("one", one), ("two", two)])
        s.validate({"one": {"a": "1a", "b": "1b"}, "two": {"a": "2a", "b": "2b"}})

        s = Structure([
            ("one", Structure([
                ("a", String(validator=validatish.Required())),
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
            one = String(validator=validatish.Required())
            two = String()

        s = TestStructure()
        s.validate({"one": "One", "two": "Two"})
        self.assertRaises(Invalid, s.validate, {"one": "", "two": "Two"})

    def test_extend_meta(self):

        class TestStructure(Structure):
            one = String(validator=validatish.Required())
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
        s = Sequence(String(validator=validatish.Required()))
        try:
            s.validate( ["",""] )
        except Invalid, e:
            return
        unittest.TestCase.fail('no exception raised')
            
    def test_validate_structure(self):
        s = Structure([('list',Sequence(String(validator=validatish.Required())))])
        try:
            s.validate( {'list':["",""]} )
        except Invalid, e:
            return
        unittest.TestCase.fail('no exception raised')


if __name__ == "__main__":
    unittest.main()

