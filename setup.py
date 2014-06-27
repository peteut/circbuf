import os
import sys
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

required_version = (3, 3)
if sys.version_info < required_version:
    raise SystemExit('circbuf requires Python {} or later'.format(
        '.'.join(map(str, required_version))))

setup(
    name='circbuf',
    version='0.0.0',
    description='Circular Buffer for Python',
    long_description=README,
    author='Alain Péteut',
    packages=('circbuf',),
    test_suite='nose.collector',
    platforms='all'
)
