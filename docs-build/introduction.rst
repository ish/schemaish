
About Schemaish
===============

Schemaish is a schema library that was initially written to support the formish form library. However it has been designed to work as a standalone schema package with validation from validatish.

How does Schemaish work?
------------------------

There are two ways of creating schemas, the procedural way and the declarative way. Here is the procedural way.

>>> import schemaish
>>> schema = schemaish.Integer(title='My Integer', description='This is really my integer')

The schema can now be used to validate a value.. 

>>> schema.validate(10)

.. note:: Validation does not validate types, it only calls the validation that has been applied to the schema. If you need to have type validation, add a specific validator

A Schemaish Structure
---------------------

Just create a create a structure and add schema attributes to it!

>>> schema = schemaish.Structure()
>>> schema.add( 'myfield', schemaish.Integer() )
>>> schema.add( 'myotherfield', schemaish.String() )

and we can now validate a dictionary

>>> schema.validate( {'myfield': 12, 'myotherfield': 'foo'} )

.. note:: The title and description are used by Formish as the label and description of each field.

Declarative Schema Generation
-----------------------------

This will be familiar to many developers.. 

>>> class Name(Structure):
...    title = String()
...    first = String(title="First Name")
...    last = String(title="Last Name")


Validation
==========

See the validatish module documentation to learn more about the validators available.

>>> import validatish
>>> schema = schemaish.Integer(validator=validatish.Required())
>>> schema.validate(None)
...schemaish.attr.Invalid: is required
>>> schema.validate(10)











