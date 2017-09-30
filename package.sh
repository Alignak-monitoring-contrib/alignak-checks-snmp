#!/bin/sh

set -ev

gem install fpm

# Debian

if [ "$1" = "master" ]; then
   if [ "$2" = "2.7" ]; then
     fpm -s python --python-install-lib "/usr/lib/python2.7/dist-packages" -t deb -a all -d python-alignak --deb-no-default-config-files --python-install-data '/usr/local' ./setup.py
     version=`python -c "from version import __version__;print(__version__)"`
   fi
   sed -i -e "s|\"dev\"|\"${version}\"|g" .bintray.json
   sed -i -e s/alignak_deb-testing/alignak_deb-stable/g .bintray.json
elif [ "$1" = "develop" ]; then
   DEVVERSION=`date "+%Y%m%d%H%M%S"`
   if [ "$2" = "2.7" ]; then
     fpm -s python --python-install-lib "/usr/lib/python2.7/dist-packages" -t deb -a all -v $DEVVERSION-dev -d python-alignak --deb-no-default-config-files --python-install-data '/usr/local' ./setup.py
   fi
fi