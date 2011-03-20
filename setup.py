#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='PyMIME',
      version='0.2',
      description='A MIME formatter in python',
      author='Alexander Werner',
      author_email='alex@documentfoundation.org',
      url='https://github.com/awerner/pymime',
      packages=['pymime','pymime.plugins'],
      package_dir={'':'src/'},
      package_data={'pymime': ["*.conf.default"],
                    'pymime.plugins': ["*.conf.default"]},
      scripts=['src/pymimec', 'src/pymimed'],
     )
