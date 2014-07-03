import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

required_version = (3, 2)
if sys.version_info < required_version:
    raise SystemExit('circbuf requires Python {} or later'.format(
        '.'.join(map(str, required_version))))

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

SETUP_REQUIRES = []
INSTALL_REQUIRES = []
TESTS_REQUIRE = ['nose>=1.3', 'coverage>=3.7']
if sys.version_info < (3, 3):
    TESTS_REQUIRE.append('mock>=1.0')
    INSTALL_REQUIRES.append('contextlib2>=0.4')

setup(
    name='circbuf',
    version='0.0.0',
    description='circular buffer for Python',
    long_description=README,
    author='Alain Péteut',
    author_email='alain.peteut@yahoo.com',
    packages=find_packages(exclude=('tests',)),
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    test_suite='nose.collector',
    platforms='all',
    classifiers=CLASSIFIERS
)
