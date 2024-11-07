import csv
import argparse
import getpass
from cpapi import APIClientArgs, APIClient
from checkpoint_exceptions import APIError
from LoggingConfig import logger


"""
Tool to create rules on Checkpoint Management server.

Parameters:
    - FWMgmt : ip/hostname of the management server
    - Username : the login of the account you will use to log in
    - Pwd : password of said account
    - ApiKey : API key to connect instead of account/pwd
    - File : file containing the information of the rules to create

Example usage from Powershell console:
    python addrules_checkpoint.py --FWMgmt fmcserverfqdn --Username user --File addrules_model.csv
"""


def parse_arguments():
    parser = argparse.ArgumentParser(description="Checkpoint Firewall Tool",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required parameters
    parser.add_argument("--FWMgmt", help="Checkpoint Firewall Management Server (IP or Hostname).")
    parser.add_argument("--Username", help="Management administrator username.")
    parser.add_argument("--Pwd", help="Password of user account.")
    parser.add_argument("--File", help="CSV file of rules to create.")
    parser.add_argument("--ApiKey", help="Checkpoint API token.")

    user_args = parser.parse_args()
    config = vars(user_args)
    return user_args

def main():
    logger.info("---------- BEGINNING ADDRULES_CHECKPOINT.PY ----------\n")
    user_args=parse_arguments()
    if user_args.Username and not user_args.Pwd:
        user_args.Pwd = getpass.getpass("Enter password for user {}:".format(user_args.Username))
    client_args = APIClientArgs(server=user_args.FWMgmt, port=443)
    with APIClient(client_args) as client:

        if client.check_fingerprint() is False:
            print("Could not get the server's fingerprint - Check connectivity with the server.")
            exit(1)

        # login to server:
        if not user_args.ApiKey:
            login_res = client.login(user_args.Username, user_args.Pwd)
        else:
            login_res = client.login_with_api_key(user_args.ApiKey)

        if login_res.success is False:
            print("Login failed:\n{}".format(login_res.error_message))
            exit(1)

        with open(user_args.File, "r") as file:
            csv_reader = csv.DictReader(file, skipinitialspace=True, quoting=csv.QUOTE_MINIMAL)
            
            for rule in csv_reader:
                rule_name = rule["rule_name"]
                layer = rule["package"]
                source = rule["source"].split(";")
                destination = rule["destination"].split(";")
                service = rule["port"].split(";")
                install_on = rule["install-on"].split(";")
                vpn = rule["vpn"]
                action = rule["action"]
                time = rule["time"]
                track = rule["track"]
                position = rule["position"]
                section = rule["section"]
                comments = rule["comments"]

                payload = {
                    "name": rule_name,
                    "source": source,
                    "destination": destination,  
                    "vpn": vpn,
                    "service": service,
                    "action": action,
                    "track": track,
                    "comments": comments,
                    "install-on": install_on,
                    "time": time,
                    "layer": layer,
                    "position": {
                        position: section
                    }
                }

                for key, value in payload.items():
                    print("{}: {}".format(key, value))

                add_rule_response = client.api_call("add-access-rule", payload)

                if add_rule_response.success:
                    print("The rule: '{}' on section '{}' has been added successfully".format(rule_name, section))
                else:
                    print("Failed to add the access-rule: '{}' on section '{}', Error:\n{}".format(rule_name, section, add_rule_response.error_message))
                    client.api_call("logout", {})
                    raise APIError("The API call failed.")
        
        publish_res = client.api_call("publish", {})
        if publish_res.success:
            print("The changes were published successfully.")
        else:
            print("Failed to publish the changes.")
        client.api_call("logout", {})

if __name__ == "__main__":
    main()
