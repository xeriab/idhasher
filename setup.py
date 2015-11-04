#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ast
# from distutils.core import setup
from os.path import dirname, join
from codecs import open
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('IDHasher/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='IDHasher',
    version=version,
    description='Python implementation of hashids (http://www.hashids.org).',
    long_description=open(
        join(dirname(__file__), 'README.rst'), encoding='utf-8').read(),
    author='Xeriab Nabil',
    author_email='kodeburner@gmail.com',
    url='https://bitbucket.org/KodeBurner/hashid',
    license='MIT License',
    packages=['IDHasher'],
    include_package_data=True,
    zip_safe=False,
    platforms='any'
)
