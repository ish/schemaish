"""
Schema attribute types, also imported into the main package.
"""


__all__ = ['String', 'Integer', 'Float', 'Decimal', 'Date',
           'Time', 'Boolean', 'Sequence', 'Tuple', 'Structure',
           'DateTime','File', 'Invalid']


import itertools
import validatish


# Internal counter used to ensure the order of a meta structure's attributes is
# maintained.
_meta_order = itertools.count()


_MISSING = object()


class Invalid(Exception):
    """
    basic schema validation exception
    """

    def __init__(self, error_dict):
        Exception.__init__(self,error_dict)
        self.error_dict=error_dict
        m = []
        for k,v in self.error_dict.items():
            m.append( 'field "%s" %s'%(k,v.message))
        self.message = '\n'.join(m)


    def __str__(self):
        return self.message
    __unicode__ = __str__




class Attribute(object):
    """
    Abstract base class for all attribute types in the package.

    @ivar title: Title of the attribute.
    @ivar description: Optional description.
    @ivar validator: Optional FormEncode validator.
    """

    type = None
    title = None
    description = None
    validator = validatish.Always()

    def __init__(self, **k):
        """
        Create a new attribute.

        @param title: Title of the attribute.
        @keyword description: Optional description.
        @keyword validator: Optional FormEncode validator.
        """
        self._meta_order = _meta_order.next()
        title = k.pop('title', _MISSING)
        if title is not _MISSING:
            self.title = title
        description = k.pop('description', _MISSING)
        if description is not _MISSING:
            self.description = description
        validator = k.pop('validator', _MISSING)
        if validator is not _MISSING:
            self.validator = validator

    def validate(self, value):
        """
        Validate the value if a validator has been provided.
        """
        if not self.validator:
            return
        try:
            self.validator(value)
        except validatish.Invalid, e:
            raise Invalid({'':e})

    def __repr__(self):
        attributes = []
        if self.title:
            attributes.append('title=%s'%repr(self.title))
        if self.description:
            attributes.append('description=%s'%repr(self.description))
        if self.validator:
            attributes.append('validator=%s'%repr(self.validator))
        return 'schemaish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))


class String(Attribute):
    """
    A Python unicode instance.
    """
    type = 'String'


class Integer(Attribute):
    """
    A Python integer.
    """
    type='Integer'


class Float(Attribute):
    """
    A Python float.
    """
    type='Float'


class Decimal(Attribute):
    """
    A decimal.Decimal instance.
    """
    type='Decimal'


class Date(Attribute):
    """
    A datetime.date instance.
    """
    type='Date'


class Time(Attribute):
    """
    A datetime.time instance.
    """
    type='Time'


class DateTime(Attribute):
    """
    A datetime.datetime instance.
    """
    type='DateTime'


class Boolean(Attribute):
    """
    A Python Boolean instance.
    """
    type='Boolean'


class Sequence(Attribute):
    """
    A sequence (Python list) of attributes of a specific type.

    @ivar attr: Attribute type of items in the sequence.
    """
    type = 'Sequence'
    attr = None

    def __init__(self, attr=None, **k):
        """
        Create a new Sequence instance.

        @keyword attr: Attribute type of items in the sequence.
        """
        super(Sequence, self).__init__(**k)
        if attr is not None:
            self.attr = attr

    def validate(self, value):
        """
        Validate all items in the sequence and then validate the Sequence
        itself.
        """
        error_dict= {}
        if value is not None:
            for n, item in enumerate(value):
                try:
                    self.attr.validate(item)
                except Invalid, e:
                    for k, v in e.error_dict.items():
                        if k == '':
                            error_dict[str(n)] = v
                        else:
                            error_dict['%s.%s' % (str(n), k)] = v

        try:
            super(Sequence, self).validate(value)
        except Invalid, e:
            error_dict.update(e.error_dict)
            
        if error_dict:
            raise Invalid(error_dict)

    def __repr__(self):
        return 'schemaish.Sequence(%r)'%self.attr

class Tuple(Attribute):
    """
    A Python tuple of attributes of specific types.

    @ivar attrs: List of Attributes that define the items in the tuple.
    """
 
    type = 'Tuple'
    attrs = None

    def __init__(self, attrs=None, **k):
        """
        Create a Tuple instance.

        @param attrs: List of Attributes that define the items in the tuple.
        """
        super(Tuple, self).__init__(**k)
        if attrs is not None:
            self.attrs = attrs

    def add(self, attr):
        """
        Add an attribute to the tuple

        @param attr: Attribute type.
        """
        if attr is None:
            self.attrs = [attr]
        else:
            self.attrs.append(attr)

    def validate(self, value):
        """
        Validate the tuple's items and the tuple itself.
        """
        if value:
            if len(self.attrs) != len(value):
                raise Invalid({'':validatish.Invalid("Incorrect size")})
            for attr, item in zip(self.attrs, value):
                attr.validate(item)
        super(Tuple, self).validate(value)

    def __repr__(self):
        return 'schemaish.Tuple(%r)'%self.attrs


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

    >>> from schemaish import Structure, String
    >>> s1 = Structure()
    >>> s1.add("title", String())
    >>> s1.add("first", String(title="First Name"))
    >>> s1.add("last", String(title="Last Name"))

    >>> class Name(Structure):
    ...    title = String()
    ...    first = String(title="First Name")
    ...    last = String(title="Last Name")
    ...

    >>> s2 = Name()

    @ivar attrs: List of (name, attribute) tuples each of which defines the
        names and type of an attribute of the structure.
    """

    type = 'Structure'
    __metaclass__ = _StructureMeta

    def __init__(self, attrs=None, **k):
        """
        Create a new structure.

        @params attrs: List of (name, attribute) tuples defining the name and
            type of the structure's attributes.
        """
        super(Structure, self).__init__(**k)
        # If attrs has been passed as an arg then use that as the attrs of the
        # structure. Otherwise use the class's attrs, making a copy to ensure
        # that any added attrs to the instance do not get appended to te
        # class's attrs.
        if attrs is not None:
            self.attrs = attrs
        else:
            self.attrs = list(self.attrs)

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
        Validate all items in the sequence and then validate the Sequence
        itself.
        """
        error_dict = {}
        if value is not None:
            for (name, attr) in self.attrs:
                try:
                    attr.validate(value.get(name))
                except Invalid, e:
                    for k, v in e.error_dict.items():
                        if k == '':
                            error_dict[name] = v
                        else:
                            error_dict['%s.%s' % (name, k)] = v
        try:
            super(Structure, self).validate(value)
        except Invalid, e:
            error_dict.update(e.error_dict)
            
        if error_dict:
            raise Invalid(error_dict)

    def __repr__(self):
        item = '"%s": %s'
        attrstrings = [item%a for a in self.attrs]
        return 'schemaish.Structure(%s)'%(', '.join(attrstrings))


class File(Attribute):
    """
    A File Object
    """
    type = 'File'

