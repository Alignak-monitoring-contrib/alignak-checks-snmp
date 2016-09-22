#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import datetime
del os.link
import fileinput

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


def get_alignak_cfg():
    """
        Search for an */usr/local/etc/default/alignak* or *etc/default/alignak* file
        and parse its content to find out Alignak main paths

        Returns a dict with the found elements and their respective value
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
              "You host is probably A BSD or DragonFly Unix system, else "
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
    """
    Overload the default copy of files
    """
    def run(self):
        """
        Overload the default copy of files:
        1/ copy the data files in their respective directories
        2/ parse each file in the to_be_parsed_files list:
            - search each line with ont of this pattern:
                ALIGNAKETC
                ALIGNAKVAR
                ALIGNAKBIN
                ALIGNAKRUN
                ALIGNAKLOG
                ALIGNAKLIB
                ALIGNAKUSER
                ALIGNAKGROUP
            - replace found pattern with the value determined for each variable
        """
        # Before data files installation ...
        # ... backup existing files
        if to_be_installed_files:
            installation_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            print "Checking former existing files..."
            for dir,file in to_be_installed_files:
                filename = os.path.join(dir, file)
                if os.path.isfile(filename):
                    bkp_file = "%s_%s%s_" % (
                        os.path.splitext(filename)[0],
                        installation_date,
                        os.path.splitext(filename)[1]
                    )
                    print " -> backing up file: %s/%s to %s" % (dir, file, bkp_file)
                    os.rename(filename, bkp_file)
                    print " -> backed up: %s/%s" % (dir, file)
                else:
                    print " -> ignoring file: %s/%s" % (dir, file)

        # Setuptools install_data ...
        _install_data.run(self)

        # After data files installation ...
        # ... parse configuration files to update installation dir
        if to_be_parsed_files:
            # Prepare pattern for alignak.cfg
            to_change = re.compile("|".join(alignak_cfg.keys()))

            print "Parsed files: "
            for dir,file in to_be_parsed_files:
                print " parsing %s%s" % (dir,file)

                # Parse file
                for line in fileinput.input(os.path.join(dir, file), inplace=True):
                    print(to_change.sub(lambda m: alignak_cfg[re.escape(m.group(0))], line))

                # Rename .parse file
                os.rename(os.path.join(dir, file), os.path.join(dir, file[:-6]))
                print " parsed %s%s" % (dir,file[:-6])

# Get default Alignak paths ...
alignak_cfg = get_alignak_cfg()
if not alignak_cfg:
    sys.exit("Alignak default paths not found!")

print "Alignak config: "
for path in alignak_cfg:
    print " %s = %s" % (path, alignak_cfg[path])

# Define installation paths
# Get Alignak root configuration directory
alignak_etc_path = alignak_cfg['ALIGNAKETC']
# Get Alignak configuration packs directory
alignak_cfg_path = os.path.join(
    alignak_cfg['ALIGNAKETC'], 'arbiter', 'packs', manifest["__checks_type__" ]
)
# Get Alignak libexec directory
alignak_libexec_path = alignak_cfg['ALIGNAKLIB']


# Build list of all installable package files
data_files = []
to_be_parsed_files = []
to_be_installed_files = []
for subdir, dirs, files in os.walk(manifest["__pkg_name__"]):
    for file in files:
        # Ignore files which name starts with __
        if file.startswith('__'):
            continue

        # Files in plugins directory will be installed in the plugins directory of Alignak
        if subdir and 'plugins' in subdir:
            data_files.append(
                (os.path.join(
                    alignak_libexec_path,
                    re.sub(
                        r"^(%s\/|%s$)" % (
                            os.path.join(manifest["__pkg_name__"], 'plugins'),
                            os.path.join(manifest["__pkg_name__"], 'plugins')
                        ),
                        "",
                        subdir
                    )
                ),
                [os.path.join(subdir, file)])
            )
            to_be_installed_files.append(
                (os.path.join(
                    alignak_libexec_path,
                    re.sub(
                        r"^(%s\/|%s$)" % (
                            os.path.join(manifest["__pkg_name__"], 'plugins'),
                            os.path.join(manifest["__pkg_name__"], 'plugins')
                        ),
                        "",
                        subdir
                    )
                ),
                file)
            )
            if file.endswith(".parse"):
                to_be_parsed_files.append(
                    (os.path.join(
                        alignak_libexec_path,
                        re.sub(
                            r"^(%s\/|%s$)" % (
                                os.path.join(manifest["__pkg_name__"], 'plugins'),
                                os.path.join(manifest["__pkg_name__"], 'plugins')
                            ),
                            "",
                            subdir
                        )
                    ),
                    file)
                )

        # Files in ALIGNAKETC directory will be installed
        # in the configuration directory of Alignak (etc/alignak)
        elif subdir and 'ALIGNAKETC' in subdir:
            data_files.append(
                (os.path.join(
                    alignak_etc_path,
                    re.sub(
                        r"^(%s\/|%s$)" % (
                            os.path.join(manifest["__pkg_name__"], 'ALIGNAKETC'),
                            os.path.join(manifest["__pkg_name__"], 'ALIGNAKETC')
                        ),
                        "",
                        subdir
                    )
                ),
                [os.path.join(subdir, file)])
            )
            to_be_installed_files.append(
                (os.path.join(
                    alignak_etc_path,
                    re.sub(
                        r"^(%s\/|%s$)" % (
                            os.path.join(manifest["__pkg_name__"], 'ALIGNAKETC'),
                            os.path.join(manifest["__pkg_name__"], 'ALIGNAKETC')
                        ),
                        "",
                        subdir
                    )
                ),
                 file)
            )
            if file.endswith(".parse"):
                to_be_parsed_files.append(
                    (os.path.join(
                        alignak_etc_path,
                        re.sub(
                            r"^(%s\/|%s$)" % (
                                os.path.join(manifest["__pkg_name__"], 'ALIGNAKETC'),
                                os.path.join(manifest["__pkg_name__"], 'ALIGNAKETC')
                            ),
                            "",
                            subdir
                        )
                    ),
                    file)
                )
        # Other files will be installed in the pack created directory (etc/alignak/packs/ME)
        # in the configuration directory of Alignak
        else:
            data_files.append(
                (
                    os.path.join(
                        alignak_cfg_path,
                        re.sub(r"^(%s\/|%s$)" %(manifest["__pkg_name__"], manifest["__pkg_name__"]), "", subdir)
                    ),
                    [os.path.join(subdir, file)]
                )
            )
            to_be_installed_files.append(
                (
                    os.path.join(
                        alignak_cfg_path,
                        re.sub(r"^(%s\/|%s$)" %(manifest["__pkg_name__"], manifest["__pkg_name__"]), "", subdir)
                    ),
                    file
                )
            )
            if file.endswith(".parse"):
                to_be_parsed_files.append(
                    (
                        os.path.join(
                            alignak_cfg_path,
                            re.sub(r"^(%s\/|%s$)" %(manifest["__pkg_name__"], manifest["__pkg_name__"]), "", subdir)
                        ),
                        file
                    )
                )

# to_be_installed_files contains tuples for the installed files
if to_be_installed_files:
    print "Installed data files: "
    for dir, file in to_be_installed_files:
        print " %s = %s" % (dir, file)

# to_be_parsed_files contains tuples for files to be parsed (directory, file)
if to_be_parsed_files:
    print "Parsed files: "
    for dir, file in to_be_parsed_files:
        print " %s = %s" % (dir,file)

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
        '': 'README.rst',
        '': 'LICENSE',
        '': [os.path.join(manifest["__pkg_name__"], '*')],
    },

    # Where to install which file ...
    # All pack files are installed at the same place.
    data_files = data_files,

    # Dependencies (if some) ...
    install_requires=[''],

    # Entry points (if some) ...
    entry_points={
    },

    cmdclass={
        'install_data': my_install_data,  # override install_data to set a post install hook
    }
)
