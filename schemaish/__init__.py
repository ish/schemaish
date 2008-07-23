"""
A high-level schema definition package, using formencode for validation.
"""


# Import all public (or at least often used) names from the schemaish package
# as well as all FormEncode validators.

from schemaish.attr import *

from formencode.validators import Invalid
from formencode.compound import All, Any
from formencode.validators import CIDR, Email, Empty, MACAddress, NotEmpty, \
        OneOf, PlainText, Regex, URL, Wrapper

