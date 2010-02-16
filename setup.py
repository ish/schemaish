from setuptools import setup, find_packages
import sys, os

version = '0.5.6'

setup(name='schemaish',
      version=version,
      description="Schemaish is a simple schema library.",
      long_description="""\
Schemaish is a simple schema library that allow the construction and validation of python data structures. Take a look at `http://schema.ish.io <http://schema.ish.io>`_ for more info.

      Changelog at `http://github.com/ish/schemaish/raw/master/CHANGELOG <http://github.com/ish/schemaish/raw/master/CHANGELOG>`_
""",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ], 
      keywords='schema,validation',
      author='Tim Parkin, Matt Goodall',
      author_email='developers@ish.io',
      url='http://schema.ish.io',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'validatish >= 0.6',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite='schemaish.tests',
      )

