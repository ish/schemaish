"""
Module of validators, also imported into the main package.

Most of the validators are actually imported directly from formencode. However,
some of the formencode validators are just silly ;-), so we leave a few
formencode validators out and add a few of our own.
"""


__all__ = [
        # Re-export FormEncode's validators.
        'All', 'Any',
        'CIDR', 'DateValidator', 'Email', 'Empty', 'MACAddress', 'MinLength',
        'MaxLength', 'NotEmpty', 'OneOf', 'PlainText', 'Regex', 'URL',
        'Wrapper',
        # Export our validators.
        'Always',
        ]


from formencode.compound import All, Any
from formencode.validators import CIDR, DateValidator, Email, Empty, \
        MinLength, MaxLength, MACAddress, NotEmpty, OneOf, PlainText, Regex, \
        URL, Wrapper


class Always(object):
    """
    A validator that always passes, mostly useful as a default.

    This validator tests False to make it seem "invisible" to discourage anyone
    bothering actually calling it.
    """

    def to_python(self, value, state=None):
        pass

    def __nonzero__(self):
        return False

