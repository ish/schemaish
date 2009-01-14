from setuptools import setup, find_packages
import sys, os

version = '0.5.2'

setup(name='schemaish',
      version=version,
      description="Schemaish is a simple schema library.",
      long_description="""\
Schemaish is a simple schema library that allow the construction and validation of python data structures.

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
      url='http://ish.io/projects/show/schemaish',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'validatish',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
