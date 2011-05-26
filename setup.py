#! /usr/bin/env python
# -*- coding: utf-8 -*-

import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

setup(name='PyMIME',
      version='0.2',
      description='A MIME formatter in python',
      author='Alexander Werner',
      author_email='alex@documentfoundation.org',
      url='https://github.com/awerner/pymime',
      license="GPL",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Filters',
        'Topic :: Utilities',
        ],
      install_requires = ["django"],
      packages=find_packages(),
      package_data={'pymime': ["*.conf.default"],
                    'pymime.plugins': ["*.conf.default", "footer.en"],
                    'pymime.django_app.pymime_attachmentservice': ["templates/*", "static/*"]},
      scripts=['pymimec', 'pymimed'],
      data_files=[("/etc/pymime", ["pymime/pymime.conf.default",
                                   "pymime/plugins/plugin_attachmentservice.conf.default",
                                   "pymime/plugins/plugin_footer.conf.default",
                                   "pymime/plugins/footer.en"])],
     )
