# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

from circbuf import __version__

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as readme:
    long_description = readme.read()

REQUIRED_VERSION = (3, 2)
if sys.version_info < REQUIRED_VERSION:
    raise SystemExit('circbuf requires Python {} or later'.format(
        '.'.join(map(str, REQUIRED_VERSION))))

classifiers = (
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python 3',
    'Programming Language :: Python 3.2',
    'Programming Language :: Python 3.3',
    'Programming Language :: Python 3.4',
)

install_requires = []
if sys.version_info < (3, 3):
    install_requires.append('contextlib2>=0.4')

setup(
    name='circbuf',
    version=__version__,
    description='circular buffer for Python',
	license='MIT',
    long_description=long_description,
    author='Alain Péteut',
    author_email='alain.peteut@yahoo.com',
    classifiers=classifiers,
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
    platforms='all',
)
