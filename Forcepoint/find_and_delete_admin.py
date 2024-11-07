import argparse, csv, getpass, json

from smc.elements.user import AdminUser, ApiClient
from smc import session
from LoggingConfig import logger


def parse_arguments():
    parser = argparse.ArgumentParser(description="Forcepoint Firewall Tool",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required parameters
    parser.add_argument("--FWMgmt", help="Firewall management servers, comma seperated.")
    parser.add_argument("--ID", help="ID of admin to search for.")
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


def find_admin_on_server(id, svr):
    if AdminUser.objects.filter(name=id, exact_match=True):
        return svr
    else:
        return None


def delete_admin_on_server(id, svr):
    return_code = 0
    adm = AdminUser.objects.filter(name=id, exact_match=True)
    if adm:
        if adm.enabled:
            AdminUser(id).enable_disable()
        AdminUser(id).delete()



def main():
    return_code = 0
    user_args = parse_arguments()

    connectionDictionary = user_args.APIDictionary
    loggedin = False
    present_server_list = []
    server_count = 0
    for server in user_args.FWMgmt.split(','):
        url = "http://" + server + ":8082"
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
        logger.info("Checking if admin %s exists on %s..." % (row["name"], server))
        
        res_find = find_admin_on_server(user_args.ID, server)
        if res_find:
            present_server_list.append(res_find)
        server_count += 1
        
    logger.info("Finished searching for %s." % user_args.ID)
    if len(present_server_list) > 0:
        print("Account {} found on servers:".format(user_args.ID))
        for svr in present_server_list:
            print(svr)
        logger.info("Found %s on servers %s" % (user_args.ID, str(present_server_list)))
        delete = input("Would you like to delete found accounts? [y/n]")
        if delete == "y":
            for svr in present_server_list:
                res_del = delete_admin_on_server(user_args.ID, svr)
        
    else:
        logger.info("No instances of %s found on listed servers." % user_args.ID)

    print()



if __name__ == "__main__":
    main()
