from read_config import read_ms_config
import json
import logging
import requests
import msal

config=read_ms_config()
#print(config)

def get_names_micro(surname):

    names=[]

    # Optional logging
    # logging.basicConfig(level=logging.DEBUG)

    #config = json.load(open("config.json"))
    print(config)

    # Create a preferably long-lived app instance which maintains a token cache.
    app = msal.ConfidentialClientApplication(
        config["client_id"], authority=config["authority"],
        client_credential=config["secret"],
        # token_cache=...  # Default cache is in memory only.
                        # You can learn how to use SerializableTokenCache from
                        # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
        )

    # The pattern to acquire a token looks like this.
    result = None

    # Firstly, looks up a token from cache
    # Since we are looking for token for the current app, NOT for an end user,
    # notice we give account parameter as None.
    url=[config["scope"]]
    result = app.acquire_token_silent(url, account=None)

    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
        result = app.acquire_token_for_client(scopes=config["scope"])

    endpoint="""https://graph.microsoft.com/v1.0/users?$search="surname:%s"&$orderby=displayName """ % (surname)

    if "access_token" in result:
        # Calling graph using the access token
        graph_data = requests.get(  # Use token to call downstream service
            endpoint,
            headers={'Authorization': 'Bearer ' + result['access_token'], "ConsistencyLevel":"eventual"},).json()

        output = graph_data
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You may need this when reporting a bug
        

    spe=output["value"]
    for user in spe:
        names.append(user["displayName"])

    return names