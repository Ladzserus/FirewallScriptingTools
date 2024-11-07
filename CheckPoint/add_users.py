import csv
import argparse
import getpass
from cpapi import APIClientArgs, APIClient
from checkpoint_exceptions import APIError
from LoggingConfig import logger


"""
Tool to create users on Checkpoint Management servers.

Parameters:
    - FWMgmt : ip/hostname of the management servers, comma separated
    - Username : the login of the account you will use to log in
    - Pwd : password of said account
    - ApiKey : API key to connect instead of account/pwd
    - File : file containing the information of the hosts to create

Example usage from Powershell console:
    python addhosts_checkpoint.py --FWMgmt fmcserverfqdn --Username username --File addhosts_model.csv
"""

def parse_arguments():
    parser = argparse.ArgumentParser(description="Checkpoint Firewall Tool",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required parameters
    parser.add_argument("--FWMgmt", help="Checkpoint Firewall Management Servers (IP or Hostname), comma separated.")
    parser.add_argument("--Username", help="Management administrator username.")
    parser.add_argument("--Pwd", help="Password of user account.")
    parser.add_argument("--File", help="CSV file of hosts to create.")
    parser.add_argument("--ApiKey", help="Checkpoint API tokens, comma separated.")

    user_args = parser.parse_args()
    config = vars(user_args)
    return user_args

def main():
    logger.info("---------- BEGINNING ADDUSERS_CHECKPOINT.PY ----------\n")
    user_args=parse_arguments()
    if user_args.Username and not user_args.Pwd:
        user_args.Pwd = getpass.getpass("Enter password for user {}:".format(user_args.Username))
    if user_args.ApiKey:
        apiKeys = user_args.ApiKey.split(",")
    server_count=0
    for server in user_args.FWMgmt.split(","):
        client_args = APIClientArgs(server=server, port=443)
        with APIClient(client_args) as client:

            if client.check_fingerprint() is False:
                logger.error("Could not get the server's fingerprint - Check connectivity with the server.")
                exit(1)

            # login to server:
            if not user_args.ApiKey:
                login_res = client.login(user_args.Username, user_args.Pwd, domain="System Data")
            else:
                login_res = client.login_with_api_key(apiKeys[server_count], domain="System Data")

            if login_res.success is False:
                logger.error("Login failed:\n%s" % login_res.error_message)
                continue

            with open(user_args.File, "r") as file:
                csv_reader = csv.DictReader(file, skipinitialspace=True, quoting=csv.QUOTE_MINIMAL)
                for user in csv_reader:
                    user_id = user["user_id"]
                    full_name = user["full_name"]
                    perms = user["perms"]

                    payload = {
                        "name": group_name,
                        "comments" : full_name,
                        "authentication-method" : "radius",
                        "radius-server": "Radius_Server_Object",
                        "permissions-profile": perms
                    }

                    add_user_response = client.api_call("add-administrator", payload)

                    if add_group_response.success:
                        print("The group: '{}' has been added successfully".format(group_name))
                    else:
                        print("Failed to add the group: '{}', Error:\n{}".format(group_name, add_group_response.error_message))
                        client.api_call("logout", {})
                        raise APIError("The API call failed.")

            # Publish the changes
            publish_res = client.api_call("publish", {})
            if publish_res.success:
                print("The changes were published successfully.")
            else:
                print("Failed to publish the changes.")
            client.api_call("logout", {})
            server_count+=1


if __name__ == "__main__":
    main()
        
