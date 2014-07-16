# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from circbuf import __version__

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as readme:
    long_description = readme.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python 3',
    'Programming Language :: Python 3.2',
    'Programming Language :: Python 3.3',
    'Programming Language :: Python 3.4',
]

install_requires = []
if sys.version_info < (3, 3):
    install_requires.append('contextlib2>=0.4')

tests_require=['tox>=1.7.2'],


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v']
        self.test_suite = True

    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


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
    tests_require=tests_require,
    cmdclass={'test': Tox},
    platforms='all',
)
