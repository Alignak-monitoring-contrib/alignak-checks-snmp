#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import datetime
del os.link
from alignak_setup.tools import get_alignak_cfg, get_files, get_to_be_installed_files, parse_files

try:
    import distutils.core
    from distutils.command.install_data import install_data as _install_data

    from setuptools import setup, find_packages
    from setuptools.command.install import install as _install
    from setuptools.command.develop import develop as _develop
except:
    sys.exit("Error: missing python-setuptools library")

try:
    python_version = sys.version_info
except:
    python_version = (1, 5)
if python_version < (2, 7):
    sys.exit("This application requires a minimum Python 2.7.x, sorry!")
elif python_version >= (3,):
    sys.exit("This application is not yet compatible with Python 3.x, sorry!")


# Better to use exec to load the package information from a version.py file
# so to not have to import the package. as of it, the setup.py do not need to be modified
# for each package that is built from this one...
with open(os.path.join('version.py')) as fh:
    manifest = {}
    exec(fh.read(), manifest)


# Overloading setup.py install_data
class my_install_data(_install_data):
    def run(self):
        """
        Overload the default copy of files
        """
        self.data_files = get_to_be_installed_files(self.data_files)

        # Setuptools install_data ...
        _install_data.run(self)

        # After data files installation ...
        # ... parse configuration files to update installation dir
        if self.data_files:
            parse_files(to_be_parsed_files, alignak_cfg)


# Get default Alignak paths ...
alignak_cfg = get_alignak_cfg()
if not alignak_cfg:
    sys.exit("Alignak default paths not found!")

# Build list of all installable package files
(data_files, to_be_parsed_files, to_be_installed_files) = get_files(
    alignak_cfg, manifest["__pkg_name__"], manifest["__checks_type__"]
)

for df in data_files:
    print df

setup(
    name=manifest["__pkg_name__"],
    version=manifest["__version__"],

    # Metadata for PyPI
    author=manifest["__author__"],
    author_email=manifest["__author_email__"],
    keywords="alignak monitoring pack checks " + manifest["__checks_type__"],
    url=manifest["__url__"],
    license=manifest["__license__"],
    description=manifest["__description__"],
    long_description=open('README.rst').read(),

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration'
    ],

    # Unzip Egg
    zip_safe=False,

    # Package data
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'my_package': [os.path.join(manifest["__pkg_name__"], '*')],
    },

    # Where to install which file ...
    # All pack files are installed at the same place.
    data_files = data_files,

    # Dependencies (if some) ...
    install_requires=['alignak_setup'],

    # Entry points (if some) ...
    entry_points={
    },

    cmdclass={
        'install_data': my_install_data,  # override install_data to set a post install hook
    }
)
