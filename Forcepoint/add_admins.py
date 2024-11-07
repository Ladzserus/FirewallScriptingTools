import argparse, csv, getpass, json

from smc.elements.user import AdminUser, ApiClient
from smc import session
from LoggingConfig import logger


def parse_arguments():
    parser = argparse.ArgumentParser(description="Forcepoint Firewall Tool",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required parameters
    parser.add_argument("--FWMgmt", help="Firewall management servers, comma seperated.")
    parser.add_argument("--File", help="CSV file of admins to create.")
    parser.add_argument("--LoginType", choices=["user", "apikey"], help="Login method")

    # Optional parameters
    parser.add_argument("--User", "-u", help="Login of user to connect to the SMC.")
    parser.add_argument("--APIKeys", "-k", help="List of comma seperated API Keys (same order as servers).")
    parser.add_argument("--APIDictionary", "-d", help="Dictionary of servers and API keys.", type=json.loads) # Pass a string here (for ex.: a json.dumps(dictionary))

    user_args = parser.parse_args()
    validate_arguments(parser, user_args)
    config = vars(user_args)
    return user_args


def validate_arguments(parser, user_args):
    if user_args.LoginType == "user" and user_args.User is None:
        user_args.User = input("Enter the user to connect to the SMC: ")
    if len(user_args.FWMgmt.split(",")) != len(user_args.APIKeys.split(",")):
        logger.warning("Mismatching number of servers and API keys.")


def main():
    return_code = 0
    user_args=parse_arguments()

    try:
        with open(user_args.File, "r") as file:
            csv_reader = csv.DictReader(file, skipinitialspace=True, quoting=csv.QUOTE_MINIMAL)
            connectionDictionary = user_args.APIDictionary
            current_server = ""
            loggedin = False
            server_count = 0
            for server in user_args.FWMgmt.split(","):
                server_URL = "http://" + server + ":8082"
                logger.info("Logging in to Forcepoint SMC %s..." % server)
                # Login
                if user_args.LoginType == "user":
                    password = getpass.getpass("Enter password for API user {}:".format(user_args.User))
                    session.login(url=server_URL, login=user_args.User, pwd=password)
                    loggedin = True
                elif user_args.LoginType == "apikey":
                    if user_args.APIDictionary:
                        session.login(url=server_URL, api_key=connectionDictionary[server])
                    else:    
                        api_key = user_args.APIKeys.split(",")[server_count]
                        session.login(url=server_URL, api_key=api_key)
                    loggedin = True
                else:
                    logger.error("No authentication method was supplied for log in.")
                    raise Exception("No authentication method supplied.")

                logger.info("Login successful.")
                logger.info("Checking if admin %s already exists..." % row["name"])
                # Check if the admin already exists
                if AdminUser.objects.filter(name=admin["name"], exact_match=True):
                    logger.error("\tThis account already exists on SMC %s. Skipping..." % server)
                    continue

                # Create the admin account with RADIUS authentication
                admin_res = AdminUser.create(row["name"], superuser=True, auth_method="ADS", comment=row["fullname"])
                logger.info("Admin %s created successfully." % row["name"])
                session.logout()
                server_count += 1


    except BaseException as e:
        logger.error("An error occurred: %s" % str(e))
        return_code = 1
    finally:
        logger.info("Operations complete, logging out...")
        session.logout()
        logger.info("Closing tool with return code %s." % str(return_code))
        return return_code


if __name__ == "__main__":
    main()