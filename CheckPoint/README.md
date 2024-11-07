# Checkpoint Firewall Python scripts

This folder hosts some scripts that can be used to manage common tasks on Checkpoint NGFW products via the Management API.

## Dependencies

* [The Official CheckPoint Management API Python library](https://github.com/CheckPointSW/cp_mgmt_api_python_sdk)
* [Argparse](https://github.com/python/cpython/blob/3.13/Lib/argparse.py)

## Functions

* add_rules.py: This script adds the rules in the supplied add_rules_model.csv template to the specified policy package Access Layer.
* add_users.py: This script adds the users in the supplied add_users_model.csv template to the specified FMC.
* update_srcobjs.py: This script parses a given Access Layer for references to existing specified sources and adds another specified source where it finds them.

## Usage

### add_rules.py

First, configure the CSV file with the rules to be added.

Then, call the script:
```Python
>>> python add_rules.py --FWMgmt "192.168.0.1" --File "add_rules_model.csv" --ApiKey "enteryourAPIkeyhere=="
```

### add_users.py

First, configure the CSV file with the users to be added.

Then, call the script:
```Python
>>> python add_rules.py --FWMgmt "192.168.0.1,10.0.1.1" --File "add_users_model.csv" --ApiKey "firstAPIkeyhere==,secondAPIkeyhere=="
```

## update_srcobjs.py

This script's parameters are hardcoded because I'm lazy.

```Python
>>> python update_srcobjs.py
```

## Changelog

### Initial version

Uploaded.
