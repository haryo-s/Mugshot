"""
ANALYZER

This script will analyze the dataset collected by Collector 
and it will go through all the images.

If it finds and is able to encode a face, it will add it to a JSON file.

A single JSON object will contain the following information:
    Unique ID
    Face encoding
    Charges
"""

import face_recognition
import json
import glob
import os
import numpy as np

def get_face_encoding(img_loc):
    """
    Gets the face encoding of an image. 

    :param img_loc: image location

    :return: face location as numpy array and face encoding as list, If an inappropriate amount of faces is found, then it will return None
    """
    try:
        image = face_recognition.load_image_file(img_loc)
    except Exception as error:
        print("Couldn't load image")
        pass

    face_loc = face_recognition.face_locations(image)

    face_enc = face_recognition.face_encodings(image, face_loc)
    return face_loc, face_enc

def analyze_folder(folder_location, dest_file):
    data = {}
    data['mugshots'] = []
    nr = 0

    for json_file in glob.glob(os.path.join(folder_location, '*.json'), recursive=True):
        with open(json_file) as json_string:
            json_data = json.load(json_string)
            # print(json_data)
            try:
                image_file = json_data['entries']['image']
            except Exception as error:
                pass
            file_face_loc, file_face_enc = get_face_encoding(folder_location + image_file) 

            if len(file_face_loc) == 1 and len(json_data['entries']['charges']) != 0:
                print(nr)
                # file_face_enclist = file_face_enc.tolist()
                data['mugshots'].append({
                    'unique_id': json_data['entries']['unique_id'],
                    'location': file_face_loc,
                    'encoding': file_face_enc[0].tolist(),
                    'charges': json_data['entries']['charges']
                    })
                nr += 1
                # print(file_face_enc)
            else:
                print('Entry skipped!')


    with open(dest_file, 'w') as outfile:
        json.dump(data, outfile)

analyze_folder("D:\\Photography\\CurrentProjects\\Mugshot\\mugshot\\dataset\\jailbase\\", './mugshot/dataset/datasetjailbase.json')
print("Analysis complete!")