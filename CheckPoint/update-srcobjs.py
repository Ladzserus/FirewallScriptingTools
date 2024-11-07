from cpapi import APIClient, APIClientArgs
import getpass


def login(api_server, username, password):
    client_args = APIClientArgs(server=api_server, port=443)
    client = APIClient(client_args)
    if client.check_fingerprint() is False:
        print("Could not verify server's fingerprint - check connectivity to server.")
        return None

    if not client.login(username, password):
        print("Login failed.")
        return None
    return client


def api_login(api_server, api_key):
    client_args = APIClientArgs(server=api_server, port=443)
    client = APIClient(client_args)
    if client.check_fingerprint() is False:
        print("Could not verify server's fingerprint - check connectivity to server.")
        return None

    if not client.login_with_api_key(api_key):
        print("Login failed.")
        return None
    return client


def publish_changes(client):
    publish_res = client.api_call("publish", {})
    if publish_res.success:
        print("The changes were published successfully.")
    else:
        print(f"Failed to publish the changes: {publish_res.error_message}")


def get_access_layers(client):
    layers_res = client.api_query("show-access-layers", container_key="access-layers", payload={})
    if layers_res.success:
        access_layers = []
        print("Discovered layers.")
        for layer in layers_res.data:
            access_layers.append(layer["name"])
        return access_layers
    else:
        print(f"Failed to retrieve layers: {layers_res.error_message}")
        return None


def get_policy_rules(client, policypackage):
    res = client.api_query("show-access-rulebase", details_level="full", container_key="rulebase", payload={
        "name" : policypackage,
        "use-object-dictionary" : True
    })
    if res.success:
        return res.data
    else:
        print(f"Failed to retrieve rules: {res.error_message}")
        return None


def update_source_objects(client, rule, layer, new_src):
    rule_uid = rule["uid"]
    existing_src = rule.get("source", [])

    update_src = []
    for src in existing_src:
        update_src.append(src["name"])

    if new_src in update_src:
        print(f"New source already in existing sources for rule {rule_uid}.")
        return
    
    update_src.append(new_src)
    
    res = client.api_call("set-access-rule", {
        "uid": rule_uid,
        "layer": layer,
        "source": update_src
    })

    if res.success:
        print(f"Rule {rule_uid} successfully updated with {new_src}.")
    else:
        print(f"Failed to update rule {rule_uid}: {res.error_message}.")


def mass_update(client, policypackage, new_src):
    INDIVIDUAL_OBJECTS = [
        "sample-group",
        "192.168.104.0/24",
        "192.168.105.0/24",
        "192.168.106.0/24",
        "192.168.107.0/24",
        "192.168.108.0/24",
        "192.168.109.0/24"
    ]
    rulebase = get_policy_rules(client, policypackage)
    if rulebase:
        print(f"Policy {policypackage} loaded.")
        rules_counter = 0
        for section in rulebase:
            try:
                assert section["rulebase"] is not None, f"Section contains no rules."
            except (AssertionError, KeyError):
                continue
            for rule in section["rulebase"]:
                if rule["type"] == "access-rule":
                    ruleres = client.api_call("show-access-rule", payload={"uid" : rule["uid"], "layer" : policypackage, "details-level" : "standard"})
                    if ruleres:
                        source_obj_present = False
                        for src in ruleres.data["source"]:
                            if src["name"] in INDIVIDUAL_OBJECTS:
                                source_obj_present = True
                                continue
                        if source_obj_present:
                            rules_counter += 1
                            try:
                                assert ruleres.data["name"] is not None, f"Name is undefined."
                                print(f"Flagged source object found in rule {ruleres.data['name']}")
                            except KeyError:
                                print(f"Flagged source object found in rule {ruleres.data['uid']}")
                            print(f"!!!!!UPDATING RULE WITH NEW OBJECT!!!!!")
                            update_source_objects(client, ruleres.data, policypackage, new_src)
        print(f"{rules_counter} rules modified in {policypackage}")
                    

def main():
    API_SERVER = "192.169.0.1"
    # USERNAME = "username"
    # PASSWORD = getpass.getpass("Enter password for user %s :" % USERNAME)
    API_KEY = "yourAPIkeywouldgohere=="
    POLICYPACKAGE = "PolicyPackageLayerName Network"
    NEW_SRC = "new-src-obj-to-add"

    # client = login(api_server=API_SERVER, username=USERNAME, password=PASSWORD)
    client = api_login(api_server=API_SERVER, api_key=API_KEY)

    if client:
        mass_update(client, POLICYPACKAGE, NEW_SRC)

        # This would do the update for all policy package Access Layers on the server.
        """access_layers = get_access_layers(client)
        for layer in access_layers:
            mass_update(client, layer, NEW_SRC)"""

        publish_changes(client)
        client.api_call("logout", {})


if __name__ == "__main__":
    main()
