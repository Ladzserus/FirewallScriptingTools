import argparse
import csv

from pyFMG.fortimgr import *


"""
Tool to create rules on FortiManager.

Parameters:
    - FWMgmt : ip/hostname of the management server
    - ApiKey : ApiKey for the API Admin account
    - File : file containing the information of the hosts to create

Example usage from Powershell console:
    python add_rules.py --FWMgmt serverFQDNorIP --ApiKey yourAPIkeyHERE --File add_rules_model.csv
"""


def parse_arguments():
    parser = argparse.ArgumentParser(description="Fortinet Firewall Tool",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required parameters
    parser.add_argument("--FWMgmt", help="FortiManager (IP or Hostname).")
    parser.add_argument("--ApiKey", help="API Key for FortiManager.")
    parser.add_argument("--File", help="CSV file of rules to create.")

    user_args = parser.parse_args()
    config = vars(user_args)
    return user_args

def main():
    user_args=parse_arguments()

    fortimgr = FortiManager(user_args.FWMgmt, apikey=user_args.ApiKey, check_adom_workspace=False)
    fortimgr.login()

    with open(user_args.File, "r") as file:
        csv_reader = csv.DictReader(file, skipinitialspace=True, quoting=csv.QUOTE_MINIMAL)
        
        for rule in csv_reader:
            url = "/pm/config/adom/root/pkg/{}/firewall/policy".format(rule["package"])

            # I don't know how to control what section to create the policy in. I presume by default it's created just before the cleanup rule.
            data = {
                "name": rule["name"],
                "srcintf": rule["srcintf"],
                "dstintf": rule["dstintf"],
                "destaddr": rule["destination"].split(";"),
                "srcaddr": rule["source"].split(";"),
                "service": rule["port"].split(";"),
                "action": rule["action"],
                "logtraffic": rule["logging"],
                "nat": "disable",
                "status": "enable"
            }

            print("Adding rule with data: ")
            for key, value in data.items():
                print("{}: {}".format(key, value))
            
            try:
                res = fortimgr.add(url, **data)
                if res[0] == 200:
                    print("The rule: '{}' has been added successfully to package '{}'".format(data["name"], rule["package"]))
                elif res[0] == 100:
                    print("The response was not a valid JSON file; check that the rule '{}' was created.".format(data["name"]))
            except FMGBaseException as err:
                print("Failed to add the rule: '{}', Error:\n{}".format(data["name"], err.msg))

    fortimgr.logout()

if __name__ == "__main__":
    main()