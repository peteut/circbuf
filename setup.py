import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

required_version = (3, 3)
if sys.version_info < required_version:
    raise SystemExit('circbuf requires Python {} or later'.format(
        '.'.join(map(str, required_version))))

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python 3',
    'Programming Language :: Python 3.3',
    'Programming Language :: Python 3.4',
    'Topic :: Software Development :: Libraries :: Python Modules'
)

INSTALL_REQUIRES = ('',)

setup(
    name='circbuf',
    version='0.0.0',
    description='circular buffer for Python',
    long_description=README,
    author='Alain Péteut',
    author_email='alain.peteut@yahoo.com',
    packages=find_packages(),
    setup_requires=('nose>=1.0',),
    test_suite='nose.collector',
    platforms='all',
    classifiers=CLASSIFIERS
)
