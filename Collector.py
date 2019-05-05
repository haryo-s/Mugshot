"""
COLLECTOR

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
import json
import datetime
import time

USER_KEY = ""

def get_jailbase_search(last_name, first_name, source_id, use_api_key = True):
    URL = ""
    parameters = {}

    if use_api_key == True:
        URL = "https://api-2445581323150.apicast.io:443/api/1/search/"
        parameters = {
                    'last_name': last_name,
                    'first_name': first_name,
                    'source_id': source_id,
                    'user_key': USER_KEY 
                    }
    elif use_api_key == False:
        URL = "http://www.JailBase.com/api/1/search/"
        parameters = {
                    'last_name': last_name,
                    'first_name': first_name,
                    'source_id': source_id
                    }
                
    r = requests.get(url = URL, params = parameters, )
    print(r.url)

    if r.status_code == 200:
        return r.json()
    else:
        print("Error! Server sent status code " + str(r.status_code))
        return None

def get_jailbase_recent(source_id, page, use_api_key = True):
    URL = ""
    parameters = {}

    if use_api_key == True:
        URL = "https://api-2445581323150.apicast.io:443/api/1/recent/"
        parameters = {
                    'source_id': source_id,
                    'page': page,
                    'user_key': USER_KEY 
                    }
    elif use_api_key == False:
        URL = "http://www.JailBase.com/api/1/recent/"
        parameters = {
                    'source_id': source_id,
                    'page': page
                    }

    r = requests.get(url = URL, params = parameters)
    print(r.url)
    
    if r.status_code == 200:
        return r.json()
    else:
        print("Error! Server sent status code " + str(r.status_code))
        return None

def get_jailbase_sources(use_api_key = True):
    URL = ""
    parameters = {}

    if use_api_key == True:    
        URL = "https://api-2445581323150.apicast.io:443/api/1/sources/"
        parameters = {
                    'user_key': USER_KEY 
                    }
    elif use_api_key == False:    
        URL = "http://www.JailBase.com/api/1/sources/"
        parameters = {}

    r = requests.get(url = URL, params = parameters)
    print(r.url)

    if r.status_code == 200:
        return r.json()
    else:
        print("Error! Server sent status code " + str(r.status_code))
        return None

def process_jailbase_recent(source_id, page, dest_folder, use_api_key=True, append=True):
    recent_results = get_jailbase_recent(source_id, page, use_api_key)
    if recent_results == None:
        print("Look up failed!")
        return

    if append == True:
        with open(dest_folder + 'collectedmugshots.json', 'r') as read_file:
            data = json.load(read_file)
    else:
        data = {}
        data['entries'] = []

    for x in recent_results['records']:
        booking_date = datetime.datetime.strptime(x['book_date'], "%Y-%m-%d")
        booking_image_url = x['mugshot'].replace('small/', '')
        booking_image = requests.get(booking_image_url).content

        unique_id = x['id'] + booking_date.year + booking_date.month + booking_date.day #TODO: Make check if unique_id already exists in dataset
        
        with open(dest_folder + str(unique_id) + '.jpg', 'wb') as image:
            image.write(booking_image)

        data['entries'].append({
            'unique_id': unique_id,
            'image':  str(unique_id) + '.jpg', #TODO Get image
            'charges': x['charges']
        })

        with open(dest_folder + 'collectedmugshots.json', 'w') as out_file:
            json.dump(data, out_file)

source_id_list = []
source_id_list_json = get_jailbase_sources(use_api_key=False)['records']

for source in source_id_list_json:
    if source['has_mugshots'] == True:
        source_id_list.append(source['source_id'])

first_in_list = True
for source in source_id_list:
    if first_in_list == True:
        process_jailbase_recent(source, 1, './mugshot/dataset/jailbase/', use_api_key=False, append=False)
        first_in_list = False
        time.sleep(2)
    else:
        process_jailbase_recent(source, 1, './mugshot/dataset/jailbase/', use_api_key=False, append=True)
        time.sleep(2)


# process_jailbase_recent('az-mcso', 1, './mugshot/dataset/jailbase/', use_api_key=False, append=False)
# time.sleep(2)
# process_jailbase_recent('ky-mgrj', 1, './mugshot/dataset/jailbase/', use_api_key=False, append=True)


