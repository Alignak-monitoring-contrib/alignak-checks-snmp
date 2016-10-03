Alignak checks package for SNMP
===============================

Checks pack for monitoring hosts with SNMP


Installation
------------

From PyPI
~~~~~~~~~
To install the package from PyPI:
::
   pip install alignak-checks-snmp


From source files
~~~~~~~~~~~~~~~~~
To install the package from the source files:
::
   git clone https://github.com/Alignak-monitoring-contrib/alignak-checks-snmp
   cd alignak-checks-snmp
   sudo python setup.py install


Documentation
-------------

Configuration
~~~~~~~~~~~~~
Edit the */usr/local/etc/alignak/arbiter/packs/wmi/resources.cfg* file and configure the domain name, user name and password allowed to access remotely to the monitored hosts WMI.
::
   #-- Default SNMP community
   $SNMPCOMMUNITYREAD$=public

Prepare host
~~~~~~~~~~~~
Some operations are necessary on the monitored hosts if SNMP remote access is not yet activated.
::
   # Install local SNMP agent
   su -
   apt-get update
   apt-get install snmpd

   # Allow SNMP get - this configuration is intended for tests puuposes
   # You should set up a more secure configuration and not allow everyone to see everything :)
   vi /etc/snmp/snmpd.conf
   =>
      #  Listen for connections from the local system only
      #agentAddress  udp:127.0.0.1:161
      #  Listen for connections on all interfaces (both IPv4 *and* IPv6)
      agentAddress udp:161,udp6:[::1]:161
   =>
      # rocommunity public  default    -V systemonly
      rocommunity public
   # Restart SNMP agent
   /etc/init.d/snmpd restart

Test remote access with the plugins files:
::
   $ /usr/local/var/libexec/alignak/check_snmp_mem.pl -H 127.0.0.1 -C public -w 80,80 -c 90,95
   Ram : 71%, Swap : 58% : ; OK


Alignak configuration
~~~~~~~~~~~~~~~~~~~~~

To define the SNMP community to be used per default, edit the *resources.cfg* file and change the default value.
::
    $SNMPCOMMUNITYREAD$=public


You simply have to tag the concerned hosts with the template `linux-snmp`.
::

    define host{
        use                     linux-snmp
        host_name               host_snmp
        address                 127.0.0.1
    }


The main `linux-snmp` template declares macros used to configure the launched checks. The default values of these macros listed hereunder can be overriden in each host configuration.
::

    _SNMPCOMMUNITY      $SNMPCOMMUNITYREAD$
    _SNMP_MSG_MAX_SIZE  65535

    _LOAD_WARN          2,2,2
    _LOAD_CRIT          3,3,3
    _STORAGE_WARN       90
    _STORAGE_CRIT       95
    _CPU_WARN           80
    _CPU_CRIT           90
    _MEMORY_WARN        80,80
    _MEMORY_CRIT        95,95
    _NET_IFACES         eth\d+|em\d+
    _NET_WARN           90,90,0,0,0,0
    _NET_CRIT           0,0,0,0,0,0


To set a specific value for an host, declare the same macro in the host definition file.
::

    define host{
        use                     linux-snmp
        host_name               host_snmp
        address                 127.0.0.1

        # Specific values for this host
        # Change warning and critical alerts level for memory
        # Same for CPU, ALL_CPU, DISK, LOAD, NET, ...
        _LOAD_WARN       3,3,3
        _LOAD_CRIT       5,5,5
    }


Bugs, issues and contributing
-----------------------------

Contributions to this project are welcome and encouraged ... issues in the project repository are the common way to raise an information.

License
-------

Alignak Pack Checks SNMP is available under the `GPL version 3 license`_.

.. _GPL version 3 license: http://opensource.org/licenses/GPL-3.0