import argparse
import csv
import getpass

from pyFMG.fortimgr import *


"""
Tool to create groups on FortiManager.

Parameters:
    - FWMgmt : ip/hostname of the management server
    - ApiKey : ApiKey for the API Admin account
    - File : file containing the information of the hosts to create

Example usage from Powershell console:
    python add_hosts.py --FWMgmt serverFQDNorIP --ApiKey yourAPIkeyHERE --File add_hosts_model.csv
"""


def parse_arguments():
    parser = argparse.ArgumentParser(description="Fortinet Firewall Tool",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required parameters
    parser.add_argument("--FWMgmt", help="FortiManager (IP or Hostname).")
    parser.add_argument("--ApiKey", help="API Key for FortiManager.")
    parser.add_argument("--File", help="CSV file of hosts to create.")

    user_args = parser.parse_args()
    config = vars(user_args)
    return user_args

def main():
    user_args=parse_arguments()

    fortimgr = FortiManager(user_args.FWMgmt, apikey=user_args.ApiKey, check_adom_workspace=False)
    fortimgr.login()
    url = "/pm/config/global/obj/firewall/address"

    with open(user_args.File, "r") as file:
        csv_reader = csv.DictReader(file, skipinitialspace=True, quoting=csv.QUOTE_MINIMAL)
        
        for host in csv_reader:
            data = {}
            data["name"] = host["name"]
            data["subnet"] = host["subnet"]

            print("Adding host with data: ")
            for key, value in data.items():
                print("{}: {}".format(key, value))
            
            # call here
            try:
                res = fortimgr.add(url, **data)
                if res[0] == 200:
                    print("The host: '{}' has been added successfully".format(data["name"]))
                elif res[0] == 100:
                    print("The response was not a valid JSON file; check that the host '{}' was created.".format(data["name"]))
            except FMGBaseException as err:
                print("Failed to add the host: '{}', Error:\n{}".format(data["name"], err.msg))

    fortimgr.logout()

if __name__ == "__main__":
    main()