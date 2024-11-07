# Forcepoint NGFW Python scripts

This folder hosts some scripts that can be used to manage common tasks on Forcepoint NGFW products via the SMC API.

## Dependencies

* [Forcepoint official SMC API Python library](https://github.com/Forcepoint/fp-NGFW-SMC-python)
* [Argparse](https://github.com/python/cpython/blob/3.13/Lib/argparse.py)

## Functions

* add_admins.py: Create administrator accounts as defined in the provided csv file on the specified Forcepoint SMC servers.
* find_and_delete_admin.py: Find (and optionally delete) administrators on specified Forcepoint SMC servers.

## Usage

### add_admins.py

First, configure the CSV file with the users to be added.

Then, call the script:
```Python
>>> add_admins.py --FWMgmt "server1fqdnorIP,server2fqdnorIP" --File "Path\to\csv\file.csv" --LoginType "apikey" --APIKeys "server1apikeyhere==,server2apikeyhere=="
```

Optional parameters:

* Authentication can be done by User / Password (--User + getpass()) - they must be identical on all supplied servers.
* A connection dictionary can be provided for easier management of API keys (--APIDictionary) - format is {"serverfqdn" : "APIKey=="}

### find_and_delete_admin.py

```Python
>>> add_admins.py --FWMgmt "server1fqdnorIP,server2fqdnorIP" --ID "adminID" --LoginType "apikey" --APIKeys "server1apikeyhere==,server2apikeyhere=="
```

Optional parameters:

* Authentication can be done by User / Password (--User + getpass()) - they must be identical on all supplied servers.
* A connection dictionary can be provided for easier management of API keys (--APIDictionary) - format is {"serverfqdn" : "APIKey=="}

## Changelog

### Initial version

Uploaded.
