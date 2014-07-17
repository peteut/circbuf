#!/usr/bin/env python

import sys
from setuptools import setup

install_requires = []
if sys.version_info < (3, 3):
    install_requires.append('contextlib2>=0.4')

setup(
    install_requires=install_requires,
    platforms='all',
    setup_requires=['pbr'],
    pbr=True,
)
