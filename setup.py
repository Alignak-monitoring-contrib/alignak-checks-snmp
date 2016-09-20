#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
del os.link
from importlib import import_module
import fileinput
import getpass
from string import Template

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


# Import pack information
from alignak_checks_snmp import __version__, __author__, __author_email__, __copyright__
from alignak_checks_snmp import __license__, __url__, __checks_type__
from alignak_checks_snmp import __name__ as __pkg_name__
package = import_module(__pkg_name__)


def get_alignak_cfg():
    """
        Search for an etc/default/alignak file and parse the file to find out Alignak main paths

        Returns a dict
    """
    alignak_cfg = {
        'ALIGNAKETC': '/usr/local/etc/alignak',
        'ALIGNAKVAR': '/usr/local/var/lib/alignak',
        'ALIGNAKBIN': '/usr/local/bin',
        'ALIGNAKRUN': '/usr/local/var/run/alignak',
        'ALIGNAKLOG': '/usr/local/var/log/alignak',
        'ALIGNAKLIB': '/usr/local/var/libexec/alignak',
        'ALIGNAKUSER': 'alignak',
        'ALIGNAKGROUP': 'alignak'
    }

    # Search Alignak main configuration file
    alignak_etc_default = None
    if os.path.isfile("/usr/local/etc/default/alignak"):
        alignak_etc_default = "/usr/local/etc/default/alignak"
    elif os.path.isfile("/etc/default/alignak"):
        alignak_etc_default = "/etc/default/alignak"
    else:
        print("Alignak 'default/alignak' file not found. "
              "You host is probably A Bsd or DragonFly Unix system, else "
              "Alignak is not installed on this host!\n"
              "Assuming Unix standard file structure based on /usr/local")
        return alignak_cfg

    # Parse Alignak configuration file
    with open(alignak_etc_default, "r") as etc_file:
        for line in etc_file:
            line = line.strip()

            if line.startswith('ETC'):
                alignak_cfg['ALIGNAKETC'] = line.split('=')[1]
            elif line.startswith('VAR'):
                alignak_cfg['ALIGNAKVAR'] = line.split('=')[1]
            elif line.startswith('BIN'):
                alignak_cfg['ALIGNAKBIN'] = line.split('=')[1]
            elif line.startswith('RUN'):
                alignak_cfg['ALIGNAKRUN'] = line.split('=')[1]
            elif line.startswith('LOG'):
                alignak_cfg['ALIGNAKLOG'] = line.split('=')[1]
            elif line.startswith('LIB'):
                alignak_cfg['ALIGNAKLIB'] = line.split('=')[1]
            elif line.startswith('ALIGNAKUSER'):
                alignak_cfg['ALIGNAKUSER'] = line.split('=')[1]
            elif line.startswith('ALIGNAKGROUP'):
                alignak_cfg['ALIGNAKGROUP'] = line.split('=')[1]
        etc_file.close()

    # Check Alignak configuration directory
    if not os.path.exists(alignak_cfg['ALIGNAKETC']):
        print("Alignak configuration directory (%s) not found: "
              "does not seem to be installed on this host!" % alignak_cfg['ALIGNAKETC'])
        return None

    # Check Alignak plugins directory
    if not os.path.exists(alignak_cfg['ALIGNAKLIB']):
        print("Alignak plugins directory (%s) not found: "
              "does not seem to be installed on this host!" % alignak_cfg['ALIGNAKLIB'])
        return None

    return alignak_cfg


# Overloading setup.py install_data
class my_install_data(_install_data):
    def run(self):
        # Setuptools install_data ...
        _install_data.run(self)

        # After data files installation ...
        # ... parse configuration files to update installation dir
        if parsed_files:
            # Prepare pattern for alignak.cfg
            to_change = re.compile("|".join(alignak_cfg.keys()))

            print("Parsed files: ")
            for dir, file in parsed_files:
                print(" parsing %s%s" % (dir,file))

                # Parse file
                for line in fileinput.input(os.path.join(dir, file), inplace=True):
                    print(to_change.sub(lambda m: alignak_cfg[re.escape(m.group(0))], line))

                # Rename .parse file
                os.rename(os.path.join(dir, file), os.path.join(dir, file[:-6]))
                print(" parsed %s%s" % (dir,file[:-6]))

# Get default Alignak paths ...
alignak_cfg = get_alignak_cfg()
if not alignak_cfg:
    sys.exit("Alignak default paths not found!")

print "Alignak configuration: "
for path in alignak_cfg:
    print(" %s = %s" % (path, alignak_cfg[path]))

# Define installation paths
# Get Alignak root installation directory
alignak_etc_path = alignak_cfg['ALIGNAKETC']
# Get Alignak configuration packs directory
alignak_cfg_path = os.path.join(alignak_cfg['ALIGNAKETC'], 'arbiter_cfg', 'packs', __checks_type__)
# Get Alignak libexec directory
alignak_libexec_path = alignak_cfg['ALIGNAKLIB']


# Build list of all installable package files
data_files = []
parsed_files = []
for subdir, dirs, files in os.walk(__pkg_name__):
    for file in files:
        if not file.startswith('__'):
            if subdir and 'plugins' in subdir:
                data_files.append(
                    (
                        os.path.join(
                            alignak_libexec_path,
                            re.sub(
                                r"^(%s\/|%s$)" % (
                                    os.path.join(__pkg_name__, 'plugins'),
                                    os.path.join(__pkg_name__, 'plugins')
                                ),
                                "",
                                subdir
                            )
                        ),
                        [os.path.join(subdir, file)]
                    )
                )
                if file.endswith(".parse"):
                    parsed_files.append(
                        (
                            os.path.join(
                                alignak_libexec_path,
                                re.sub(
                                    r"^(%s\/|%s$)" % (
                                        os.path.join(__pkg_name__, 'plugins'),
                                        os.path.join(__pkg_name__, 'plugins')
                                    ),
                                    "",
                                    subdir
                                )
                            ),
                            file
                        )
                    )
            elif subdir and 'ALIGNAKETC' in subdir:
                data_files.append(
                    (
                        os.path.join(
                            alignak_etc_path,
                            re.sub(
                                r"^(%s\/|%s$)" % (
                                    os.path.join(__pkg_name__, 'ALIGNAKETC'),
                                    os.path.join(__pkg_name__, 'ALIGNAKETC')
                                ),
                                "",
                                subdir
                            )
                        ),
                        [os.path.join(subdir, file)]
                    )
                )
                if file.endswith(".parse"):
                    parsed_files.append(
                        (
                            os.path.join(
                                alignak_etc_path,
                                re.sub(
                                    r"^(%s\/|%s$)" % (
                                        os.path.join(__pkg_name__, 'ALIGNAKETC'),
                                        os.path.join(__pkg_name__, 'ALIGNAKETC')
                                    ),
                                    "",
                                    subdir
                                )
                            ),
                            file
                        )
                    )
            else:
                data_files.append(
                    (
                        os.path.join(
                            alignak_cfg_path,
                            re.sub(r"^(%s\/|%s$)" %(__pkg_name__, __pkg_name__), "", subdir)
                        ),
                        [os.path.join(subdir, file)]
                    )
                )
                if file.endswith(".parse"):
                    parsed_files.append(
                        (
                            os.path.join(
                                alignak_cfg_path,
                                re.sub(r"^(%s\/|%s$)" %(__pkg_name__, __pkg_name__), "", subdir)
                            ),
                            file
                        )
                    )

# data_files contains all the installable files
if data_files:
    print("Installed files: ")
    for dir,file in data_files:
        print(" %s = %s" % (dir,file))

# parsed_files contains tuples for files to be parsed (directory, file)
if parsed_files:
    print("Parsed files: ")
    for dir,file in parsed_files:
        print(" %s = %s" % (dir,file))

setup(
    name=__pkg_name__,
    version=__version__,

    # Metadata for PyPI
    author=__author__,
    author_email=__author_email__,
    keywords="alignak monitoring pack checks " + __checks_type__,
    url=__url__,
    license=__license__,
    description=package.__doc__.strip(),
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
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Systems Administration'
    ],

    # Unzip Egg
    zip_safe=False,

    # Package data
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': 'README.rst',
        '': 'AUTHORS',
        '': 'LICENSE',
        '': [os.path.join(__pkg_name__, '*')],
    },

    # Where to install which file ...
    # All pack files are installed at the same place.
    data_files = data_files,

    # Dependencies (if some) ...
    install_requires=[''],

    # Entry points (if some) ...
    entry_points={},

    cmdclass={
        'install_data': my_install_data,  # override install_data to set a post install hook
    }
)
