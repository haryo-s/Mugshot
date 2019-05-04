#############
# COLLECTOR #
#############

"""
This script will consult with the Jailbase API, query its 2000 most recent entries and prepare it for the analyzer
Things it needs to do:
Query the API and get a list of entries
From the entry, get the following data
    Ref ID 
    Image URL and download it
    Charges

Once collected, a JSON file should be created for each entry
and its corresponding image downloaded.
The filename of the JSON and the image should be its Ref ID

One worrying thing I should watch out for is the Ref ID. 
It might be prudent to change this to an internal ID
So there is absolutely no way to trace it back.
"""

import requests

USER_KEY = ""

def jailbase_search(last_name, first_name, source_id):
    URL = "https://api-2445581323150.apicast.io:443/api/1/search/"
    parameters = {
                    'last_name': last_name,
                    'first_name': first_name,
                    'source_id': source_id,
                    'user_key': USER_KEY 
                 }
                
    r = requests.get(url = URL, params = parameters)
    if r.status_code == 200:
        return r.json()
    else:
        msg = "Error! Server sent status code " + str(r.status_code)
        return msg

def jailbase_recent(source_id, page):
    URL = "https://api-2445581323150.apicast.io:443/api/1/recent/"
    parameters = {
                    'source_id': source_id,
                    'page': page,
                    'user_key': USER_KEY 
                 }

    r = requests.get(url = URL, params = parameters)

    if r.status_code == 200:
        return r.json()
    else:
        msg = "Error! Server sent status code " + str(r.status_code)
        return msg

def jailbase_sources():
    URL = "https://api-2445581323150.apicast.io:443/api/1/source/"
    parameters = {
                    'user_key': USER_KEY 
                 }
                
    r = requests.get(url = URL, params = parameters)

    if r.status_code == 200:
        return r.json()
    else:
        msg = "Error! Server sent status code " + str(r.status_code)
        return msg

recent = jailbase_recent('az-msco', 1)
print(recent)
