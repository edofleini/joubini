#!/usr/bin/env python

from setuptools import setup

setup(name='joubini',
      version='0.1.0',
      description='Configuration storage utilities.',
      author='Quinn Raskin',
      author_email='quinn@edofleini.com',
      url='www.edofleini.com',
      packages=['joubini'],
      package_dir={'joubini': 'joubini'},
      scripts=['scripts/joubini'],
     )
