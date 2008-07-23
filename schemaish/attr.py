"""
Schema attribute types.
"""


__all__ = ["String", "Integer", "Float", "Decimal", "Date", "Time", "Sequence",
        "Tuple", "Structure"]


import itertools


# Internal counter used to ensure the order of a meta structure's attributes is
# maintained.
_meta_order = itertools.count()


class Attribute(object):
    """
    Abstract base class for all attribute types in the package.

    @ivar title: Title of the attribute.
    @ivar description: Optional description.
    @ivar validator: Optional FormEncode validator.
    """

    def __init__(self, title, description=None, validator=None):
        """
        Create a new attribute.

        @param title: Title of the attribute.
        @keyword description: Optional description.
        @keyword validator: Optional FormEncode validator.
        """
        self.title = title
        self.description = description
        self.validator = validator
        self._meta_order = _meta_order.next()

    def validate(self, value):
        """
        Validate the value if a validator has been provided.
        """
        if self.validator is None:
            return value
        return self.validator.to_python(value)


class String(Attribute):
    """
    A Python unicode instance.
    """
    pass


class Integer(Attribute):
    """
    A Python integer.
    """
    pass


class Float(Attribute):
    """
    A Python float.
    """
    pass


class Decimal(Attribute):
    """
    A decimal.Decimal instance.
    """
    pass


class Date(Attribute):
    """
    A datetime.date instance.
    """
    pass


class Time(Attribute):
    """
    A datetime.time instance.
    """
    pass


class DateTime(Attribute):
    """
    A datetime.datetime instance.
    """
    pass


class Sequence(Attribute):
    """
    A sequence (Python list) of attributes of a specific type.

    @ivar attr: Attribute type of items in the sequence.
    """

    def __init__(self, *a, **k):
        """
        Create a new Sequence instance.

        @keyword attr: Attribute type of items in the sequence.
        """
        attr = k.pop("attr")
        super(Sequence, self).__init__(*a, **k)
        self.attr = attr

    def validate(self, value):
        """
        Validate all items in the sequence and then validate the Sequence
        itself.
        """
        value = [self.attr.validate(item) for item in value]
        return super(Sequence, self).validate(value)


class Tuple(Attribute):
    """
    A Python tuple of attributes of specific types.

    @ivar attrs: List of Attributes that define the items in the tuple.
    """

    def __init__(self, *a, **k):
        """
        Create a Tuple instance.

        @param attrs: List of Attributes that define the items in the tuple.
        """
        attrs = k.pop("attrs")
        super(Tuple, self).__init__(*a, **k)
        self.attrs = attrs

    def validate(self, value):
        """
        Validate the tuple's items and the tuple itself.
        """
        value = tuple(attr.validate(item) for (attr, item) in zip(self.attrs, value))
        return super(Tuple, self).validate(value)


class _StructureMeta(type):

    def __init__(cls, name, bases, clsattrs):
        attrs = []
        for (name, value) in clsattrs.items():
            if isinstance(value, Attribute):
                attrs.append((name, value))
                del clsattrs[name]
        attrs = [(a[1]._meta_order, a) for a in attrs]
        attrs.sort()
        attrs = [i[1] for i in attrs]
        cls.attrs = attrs


class Structure(Attribute):
    """
    Python dict conforming to a fixed structure.

    The class can be used to build a structure programmatically or using meta
    class syntax. For example the following result in s1 and s2 defining the
    same structure:

        s1 = Structure("Your Name")
        s1.add("title", String("Title"))
        s1.add("first", String("First Name"))
        s1.add("last", String("Last Name"))

        class Name(Structure):
            title = String("Title")
            first = String("First Name")
            last = String("Last Name")

        s2 = Name("Your Name")

    @ivar attrs: List of (name, attribute) tuples each of which defines the
        names and type of an attribute of the structure.
    """

    __metaclass__ = _StructureMeta

    def __init__(self, *a, **k):
        """
        Create a new structure.

        @params attrs: List of (name, attribute) tuples defining the name and
            type of the structure's attributes.
        """
        attrs = k.pop('attrs', None)
        super(Structure, self).__init__(*a, **k)
        if attrs is not None:
            self.attrs = attrs

    def add(self, name, attr):
        """
        Add a names attribute to the structure.

        @param name: Attribute name.
        @param attr: Attribute type.
        """
        self.attrs.append((name, attr))

    def get(self, name):
        """
        Get the attribute with the given name.

        @param name: Name of the attribute to return.
        @raise KeyError: Attribute name could not be found.
        """
        for (attr_name, attr) in self.attrs:
            if attr_name == name:
                return attr
        raise KeyError(name)

    def validate(self, value):
        """
        Validate the structure's attributes and the structure itself.
        """
        value = dict((name, attr.validate(value[name])) for (name, attr) in self.attrs)
        return super(Structure, self).validate(value)


