import unittest

class TestAttribute(unittest.TestCase):
    def _getTargetClass(self):
        from schemaish.attr import LeafAttribute
        return LeafAttribute
        
    def _makeOne(self, **kw):
        return self._getTargetClass()(**kw)
        
    def test_defaults(self):
        import validatish
        attr = self._makeOne()
        assert not attr.title
        assert not attr.description
        assert not attr.description
        assert not attr.validator
        self.assertEqual(attr.default, None)
        assert isinstance(attr.validator, validatish.Always)

    def test_subclass(self):
        Attribute = self._getTargetClass()
        class Something(Attribute):
            title = 'Title'
            description = 'Description'
            validator = staticmethod(required)
        attr = Something()
        assert attr.title is Something.title
        assert attr.description is Something.description
        assert attr.validator is Something.validator
        attr = Something(title=None, description=None, validator=None)
        assert attr.title is None
        assert attr.description is None
        assert attr.validator is None

    def test__repr__(self):
        attr = self._makeOne(title='title',
                             default=True,
                             description='description',
                             validator=required)
        begin_expected = (
            "schemaish.LeafAttribute(title='title', "
            "description='description', validator=<function required")
        end_expected = 'default=True)'
        r = repr(attr)
        self.assertEqual(r[:len(begin_expected)], begin_expected)
        self.assertEqual(r[-len(end_expected):], end_expected)

class TestString(unittest.TestCase):
    def _getTargetClass(self):
        from schemaish import String
        return String

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_positional(self):
        self.assertRaises(TypeError, self._makeOne, "a")

    def test_title(self):
        self.assertEquals(self._makeOne(title="Title").title, "Title")

    def test_description(self):
        self.assertEquals(self._makeOne(description="Description").description,
                          "Description")

    def test_meta_order(self):
        a = self._makeOne()
        b = self._makeOne()
        self.assertTrue(a._meta_order < b._meta_order)

    def test_validate(self):
        from schemaish.attr import Invalid
        self._makeOne().validate("")
        self._makeOne().validate(None)
        self.assertRaises(
            Invalid,
            self._makeOne(validator=required).validate, None)
        self.assertRaises(
            Invalid,
            self._makeOne(validator=required).validate, "")


class TestDate(unittest.TestCase):

    def _getTargetClass(self):
        from schemaish import Date
        return Date

    def test_validate(self):
        from schemaish import Invalid
        import datetime
        today = datetime.date.today()
        Date = self._getTargetClass()
        Date().validate(None)
        Date().validate(today)
        Date(validator=required).validate(today)
        self.assertRaises(Invalid,
                          Date(validator=required).validate, None)


class TestSequence(unittest.TestCase):

    def _getTargetClass(self):
        from schemaish import Sequence
        return Sequence

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_validate(self):
        from schemaish.attr import Invalid
        s = self._makeOne(Attr())
        s.validate(None)
        s.validate([])
        s.validate(["one", "two"])
        s = self._makeOne(attr=Attr(), validator=required)
        s.validate(["one"])
        self.assertRaises(Invalid, s.validate, [])

    def test_nested_validation(self):
        from schemaish.attr import Invalid
        from schemaish.attr import Structure
        s = self._makeOne(Attr(validator=required))
        s.validate([])
        self.assertRaises(Invalid, s.validate, [""])
        s = self._makeOne(attr=Attr(validator=required))
        s.validate(['one'])
        self.assertRaises(Invalid, s.validate, [''])
        s = self._makeOne(
            Structure([('str', Attr(validator=required))]))
        s.validate([{'str': 'one'}])
        self.assertRaises(Invalid, s.validate, [{}])

    def test_subclass(self):
        from schemaish import Date
        from schemaish import String
        Sequence = self._getTargetClass()
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
        from schemaish import Invalid
        import validatish
        def fail(value):
            raise validatish.Invalid('fail')
        s = self._makeOne(Attr(validator=fail))
        try:
            s.validate([''])
            self.fail() # pragma: no cover
        except Invalid, e:
            self.assertTrue('0' in e.error_dict)

    def test__repr__(self):
        attr = self._makeOne()
        self.assertEqual(repr(attr), 'schemaish.Sequence(None)')

    def test_default(self):
        attr = self._makeOne()
        self.assertEqual(attr.default, [])

class TestTuple(unittest.TestCase):

    def _getTargetClass(self):
        from schemaish import Tuple
        return Tuple

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_validate(self):
        from schemaish.attr import Invalid
        t = self._makeOne([Attr(), Attr()])
        t.validate(None)
        t.validate(tuple())
        t.validate(("one", "two"))
        t = self._makeOne([Attr(), Attr()],
                          validator=required)
        t.validate(("one", "two"))
        self.assertRaises(Invalid, t.validate, tuple())
        t = self._makeOne([Attr(validator=required),Attr()])
        t.validate(("one", "two"))
        t.validate(("one", ""))
        self.assertRaises(Invalid, t.validate, ("", ""))

    def test_num_items(self):
        from schemaish import Invalid
        self.assertRaises(Invalid, self._makeOne(
            [Attr(), Attr()]).validate, ("one",))

    def test_subclass(self):
        from schemaish import Date
        from schemaish import String
        Tuple = self._getTargetClass()
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

    def test__repr__(self):
        attr = self._makeOne()
        self.assertEqual(repr(attr), 'schemaish.Tuple(None)')

    def test_add(self):
        attr = self._makeOne([])
        attr2 = Attr()
        add = ('name', attr2)
        attr.add(add)
        self.assertEqual(attr.attrs, [add])

    def test_add_None(self):
        attr = self._makeOne([])
        attr2 = Attr()
        add = None
        attr.add(add)
        self.assertEqual(attr.attrs, [add])

class TestStructure(unittest.TestCase):
    def _getTargetClass(self):
        from schemaish import Structure
        return Structure

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_validate_empty(self):
        s = self._makeOne([])
        s.validate({})
        s.validate({"notanattr": "bleurgh!"})

    def test_validate_extra(self):
        s = self._makeOne([("one", Attr())])
        s.validate({"one": "un", "notanattr": "Hah!"})

    def test_validate_attrs(self):
        s = self._makeOne([("one", Attr()),("two", Attr())])
        s.validate({"one": "un", "two": "deux"})

    def test_validate_structure_invalid(self):
        from schemaish import Invalid
        s = self._makeOne()
        s.validator = required
        self.assertRaises(Invalid, s.validate, None)

    def test_validate_missing_attrs(self):
        """
        Check that completely missing data validates as long as nothing is
        required.
        """
        from schemaish.attr import Invalid
        s = self._makeOne([("one", Attr()),("two", Attr())])
        s.validate({})
        s = self._makeOne([("one", Attr(validator=required)),
                           ("two", Attr())])
        self.assertRaises(Invalid, s.validate, {})

    def test_validate_nested(self):
        from schemaish import Invalid

        one = self._makeOne([("a", Attr()), ("b", Attr())])
        two = self._makeOne([("a", Attr()), ("b", Attr())])
        s = self._makeOne([("one", one), ("two", two)])
        s.validate({"one": {"a": "1a", "b": "1b"},
                    "two": {"a": "2a", "b": "2b"}})

        s = self._makeOne([
            ("one", self._makeOne([
                ("a", Attr(validator=required)),
                ("b", Attr()),
                ])),
            ])
        s.validate({"one": {"a": "1a", "b": "1b"}})
        self.assertRaises(Invalid, s.validate, {"one": {"a": "", "b": "1b"}})
        self.assertRaises(Invalid, s.validate, {"one": {"a": None, "b": "1b"}})

    def test_add(self):
        s = self._makeOne()
        s.add("one", Attr())
        s.add("two", Attr())
        s.validate({"one": "un", "two": "deux"})

    def test_get(self):
        one = Attr()
        s = self._makeOne([("one", one)])
        self.assertTrue(s.get("one") is one)
        self.assertRaises(KeyError, s.get, "two")

    def test_meta_order(self):
        klass = self._getTargetClass()

        class Test(klass):
            c = Attr()
            wibble = Attr()
            b = Attr()
            wobble = Attr()
            plop = Attr()
            a = Attr()

        self.assertEquals([a[0] for a in Test.attrs],
                          ["c", "wibble", "b", "wobble", "plop", "a"])

    def test_meta(self):
        from schemaish.attr import Invalid
        Structure = self._getTargetClass()

        class TestStructure(Structure):
            one = Attr(validator=required)
            two = Attr()

        s = TestStructure()
        s.validate({"one": "One", "two": "Two"})
        self.assertRaises(Invalid, s.validate, {"one": "", "two": "Two"})

    def test_extend_meta(self):

        Structure = self._getTargetClass()

        class TestStructure(Structure):
            one = Attr(validator=required)
            two = Attr()

        s1 = TestStructure()
        s2 = TestStructure()
        self.assertEquals(len(s1.attrs), 2)
        self.assertEquals(len(s2.attrs), 2)

        s2.add('three', Attr())
        self.assertEquals(len(s1.attrs), 2)
        self.assertEquals(len(s2.attrs), 3)

    def test_meta_inheritance(self):
        Structure = self._getTargetClass()
        class S1(Structure):
            first = Attr()
        class Mixin(object):
            pass
        class S2(Mixin, S1):
            second = Attr()
        class S3(S2):
            third = Attr()
        self.assertEquals(len(S1.attrs), 1)
        self.assertEquals([i[0] for i in S1.attrs], ['first'])
        self.assertEquals(len(S2.attrs), 2)
        self.assertEquals([i[0] for i in S2.attrs], ['first', 'second'])
        self.assertEquals(len(S3.attrs), 3)
        self.assertEquals([i[0] for i in S3.attrs],
                          ['first', 'second', 'third'])

    def test__repr__(self):
        attr = self._makeOne()
        self.assertEqual(repr(attr), 'schemaish.Structure()')
        
        
class TestRecursiveValidate(unittest.TestCase):

    def test_validate_sequence(self):
        from schemaish import Sequence
        from schemaish import String
        from schemaish.attr import Invalid
        s = Sequence(String(validator=required))
        self.assertRaises(Invalid, s.validate, ["",""])
            
    def test_validate_structure(self):
        from schemaish import Sequence
        from schemaish import String
        from schemaish import Structure
        from schemaish.attr import Invalid
        s = Structure([('list',Sequence(String(validator=required)))])
        self.assertRaises(Invalid, s.validate, {'list':["",""]})

class TestInvalid(unittest.TestCase):
    def _getTargetClass(self):
        from schemaish.attr import Invalid
        return Invalid

    def _makeOne(self, error_dict):
        return self._getTargetClass()(error_dict)

    def test___str__(self):
        class Dummy:
            message = '1'
        error_dict = {'a':Dummy()}
        d = self._makeOne(error_dict)
        self.assertEqual(str(d), 'field "a" 1')
        
    def test___unicode__(self):
        class Dummy:
            message = '1'
        error_dict = {'a':Dummy()}
        d = self._makeOne(error_dict)
        self.assertEqual(str(d), 'field "a" 1')

def required(s):
    if not s:
        import validatish
        raise validatish.Invalid(s)

def Attr(*arg, **kw):
    from schemaish.attr import Attribute
    class DummyAttribute(Attribute):
        type = 'Dummy'
    return DummyAttribute(*arg, **kw)


class TestDefaults(unittest.TestCase):

    def test_defaults(self):
        import schemaish
        address = schemaish.Structure()
        address.add('street', schemaish.String(default='Lidgett Lane'))
        address.add('city', schemaish.String(default='Leeds'))
        schema = schemaish.Structure()
        schema.add('first_names', schemaish.String(default='Tim'))
        schema.add('last_name', schemaish.String(default='Parkin'))
        schema.add('code', schemaish.Tuple( [schemaish.String(default='legs'), schemaish.Integer(default=11)] ))
        schema.add('address',address)
        self.assertEqual(schema.default, {'address': {'city': 'Leeds', 'street': 'Lidgett Lane'},
                                           'code': ('legs', 11),
                                           'first_names': 'Tim',
                                           'last_name': 'Parkin'})
