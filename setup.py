# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

REQUIRED_VERSION = (3, 2)
if sys.version_info < REQUIRED_VERSION:
    raise SystemExit('circbuf requires Python {} or later'.format(
        '.'.join(map(str, REQUIRED_VERSION))))

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python 3',
    'Programming Language :: Python 3.2',
    'Programming Language :: Python 3.3',
    'Programming Language :: Python 3.4',
    'Topic :: Software Development :: Libraries :: Python Modules'
)

setup_requires = []
install_requires = []
tests_require = ['nose>=1.3', 'coverage>=3.7']
if sys.version_info < (3, 3):
    tests_require.append('mock>=1.0')
    install_requires.append('contextlib2>=0.4')

setup(
    name='circbuf',
    version='0.0.0',
    description='circular buffer for Python',
    long_description=README,
    author='Alain Péteut',
    author_email='alain.peteut@yahoo.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    platforms='all',
    classifiers=CLASSIFIERS
)
