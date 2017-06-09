#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess

try:
    from setuptools import setup, find_packages
except:
    sys.exit("Error: missing python-setuptools library")

try:
    import distutils.cmd
    import distutils.log
    import distutils.core
    from distutils.core import setup
    from distutils.command.install_data import install_data as _install_data
except:
    sys.exit("Error: missing python-distutils library")

# Overloading setup.py install_data
class install_data(_install_data):
    """Overload the default data installation"""
    def run(self):
        """Overload the default copy of files:"""
        # self.data_files = get_to_be_installed_files(self.data_files)

        # Setuptools install_data ...
        _install_data.run(self)

        # After data files installation ...
        # ... try to find if an installer file exists
        # ... and then run this installer.
        self.announce("\n====================================================", distutils.log.INFO)
        self.announce("Searching for installation script...", distutils.log.INFO)
        for (target, origin) in self.data_files:
            for file in origin:
                if os.path.basename(file) in ['setup.sh']:
                    filename = os.path.basename(file)
                    self.announce(" - found '%s'" % (filename), distutils.log.INFO)

                    # Run found installation script
                    self.announce("\n----------------------------------------------------",
                                  distutils.log.INFO)
                    self.announce(" - running '%s'..." % (
                        os.path.join(self.install_dir, target, filename)), distutils.log.INFO)
                    exit_code = subprocess.call(os.path.join(self.install_dir, target, filename))
                    self.announce(" - result: %s" % (exit_code), distutils.log.INFO)
                    if exit_code > 0:
                        self.announce("\n****************************************************",
                                      distutils.log.INFO)
                        self.announce("Some errors were encountered during the installation \n"
                                      "script execution! Please check out the former log to \n"
                                      "get more information about the encountered problems.",
                                      distutils.log.INFO)
                        self.announce("****************************************************\n",
                                      distutils.log.INFO)
                    self.announce("----------------------------------------------------\n",
                                  distutils.log.INFO)
        self.announce("====================================================\n", distutils.log.INFO)

# Better to use exec to load the package information from a version.py file
# so to not have to import the package. as of it, the setup.py do not need to be modified
# for each package that is built from this one...
with open(os.path.join('version.py')) as fh:
    manifest = {}
    exec(fh.read(), manifest)
# The `manifest` dictionary now contains the package metadata

# Get the package name from the manifest
package_name = manifest["__pkg_name__"]

# Build list of all installable data files
# This will get:
# - all the files from the package `etc` subdir
# - all the files from the package `libexec` subdir
# - all the files from the package `json` subdir
# and will define the appropriate target installation directory
print("\n====================================================")
print("Searching for specific data files...")
data_files = []
for subdir, dirs, files in os.walk(package_name):
    if not subdir:
        continue

    target = None
    # Plugins directory
    if 'libexec' in subdir:
        target = os.path.join('var/libexec/alignak',
                              re.sub(r"^(%s\/|%s$)" % (
                                  os.path.join(package_name, 'libexec'),
                                  os.path.join(package_name, 'libexec')),
                                     "", subdir))
    # Configuration directory
    elif 'etc' in subdir:
        target = os.path.join('etc/alignak',
                              re.sub(r"^(%s\/|%s$)" % (
                                  os.path.join(package_name, 'etc'),
                                  os.path.join(package_name, 'etc')),
                                     "", subdir))

    # Backend json files directory
    elif 'json' in subdir:
        target = os.path.join('etc/alignak/backend-json',
                              re.sub(r"^(%s\/|%s$)" % (
                                  os.path.join(package_name, 'json'),
                                  os.path.join(package_name, 'json')),
                                     "", subdir))

    if target is None:
        print("Ignoring directory: %s" % (subdir))
        continue

    package_files = []
    for file in files:
        # Ignore files which name starts with __
        if file.startswith('__'):
            continue

        package_files.append(os.path.join(subdir, file))

    if package_files:
        data_files.append((target, package_files))

for (target, origin) in data_files:
    print("Target directory: %s:" % (target))
    for file in origin:
        print(" - %s" % (file))
print("====================================================\n")


setup(
    # Package name and version
    name=manifest["__pkg_name__"],
    version=manifest["__version__"],

    # Metadata for PyPI
    author=manifest["__author__"],
    author_email=manifest["__author_email__"],
    keywords="alignak monitoring pack checks " + manifest["__checks_type__"],
    url=manifest["__git_url__"],
    license=manifest["__license__"],
    description=manifest["__description__"],
    long_description=open('README.rst').read(),

    classifiers = manifest["__classifiers__"],

    # Unzip Egg
    zip_safe=False,

    cmdclass={
        "install_data": install_data
    },

    # Package data
    packages=find_packages(),

    # Where to install distributed files
    data_files = data_files,

    # Dependencies (if some) ...
    install_requires=[],

    # Entry points (if some) ...
    entry_points={
    },
)
