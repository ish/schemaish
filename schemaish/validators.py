"""
Module of validators, also imported into the package.

Most of the validators are actually imported directly from formencode. However,
some of the formencode validators are just silly ;-), so we leave a few
formencode validators out and add a few of our own.
"""


__all__ = [
        # Re-export FormEncode's validators.
        'All', 'Any', 'CIDR', 'DateValidator', 'Email', 'Empty', 'MACAddress',
        'MinLength', 'MaxLength', 'NotEmpty', 'OneOf', 'PlainText', 'Regex',
        'URL', 'Wrapper'
        ]


from formencode.compound import All, Any
from formencode.validators import CIDR, DateValidator, Email, Empty, \
        MinLength, MaxLength, MACAddress, NotEmpty, OneOf, PlainText, Regex, \
        URL, Wrapper

