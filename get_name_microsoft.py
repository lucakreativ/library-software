from read_config import read_ms_config  # --> read_config.py
import logging
import requests
import msal

config=read_ms_config()                                         #benutzt library Config-Reader für die Konfiguration

def get_names_micro(surname):                                   #bekommt Schüler-Namen bei Nachname

    names=[]

                                                                #Create a preferably long-lived app instance which maintains a token cache.
                                                                #Erstellt eine App-Instanz, die den Token im Cache(RAM) behällt
    app = msal.ConfidentialClientApplication(
        config["client_id"], authority=config["authority"],
        client_credential=config["secret"],
        )

                                                                #Verlaufsmuster zum bekommen des Tokens
    result = None

                                                                #Als erstes wird im Cache nachgeschaut

    url=[config["scope"]]                                                                                           #Endpunkt für API
    result = app.acquire_token_silent(url, account=None)                                                            #schaut nach Token im Cache

    if not result:                                                                                                  #kein Token gefunden
        logging.info("Token wurde nicht im Cache gefunden")
        result = app.acquire_token_for_client(scopes=config["scope"])                                               #bekommt Token von Microsoft

    endpoint="""https://graph.microsoft.com/v1.0/users?$search="surname:%s"&$orderby=displayName """ % (surname)    #API-Abfrage für den Nachnamen

    if "access_token" in result:                                                                                    #Token wurde gefunden/abgerufen
                                                                                                                    #Ruft graph mit dem Access-Token
        graph_data = requests.get(                                                                                  #benutzt den Token um die API aufzurufen
            endpoint,
            headers={'Authorization': 'Bearer ' + result['access_token'], "ConsistencyLevel":"eventual"},).json()

    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))             #Fehlermeldungen
        

    spe=graph_data["value"]                             #bekommt die Daten von den Namen
    for user in spe:                                    #iteriert durch die Daten
        names.append(user["displayName"])               #fügt den Namen zur Liste hinzu

    return names                                        #gibt die Namen in Liste zurück