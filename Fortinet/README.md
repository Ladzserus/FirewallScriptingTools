# Fortinet Firewall Python scripts

This folder hosts some scripts that can be used to manage common tasks on Fortinet NGFW products via the unoffical FortiManager API.

## Dependencies

* [Unofficial FortiManager API Python library](https://github.com/p4r4n0y1ng/pyfmg)
* [Argparse](https://github.com/python/cpython/blob/3.13/Lib/argparse.py)

## Functions

* add_rules.py: This script adds the rules in the supplied add_rules_model.csv template to the specified policy package Access Layer.
* add_hosts.py: This script adds the network hosts in the supplied add_hosts_model.csv template to the specified FMC.

## Usage

### add_rules.py

First, configure the CSV file with the rules to be added.

Then, call the script:
```Python
>>> add_rules.py --FWMgmt "fortmanagerFQDN" --APIKey "yourAPIkeyhere" --File "Path\to\csv\file.csv"
```
