"""
MUGSHOT

This script will take in an image and compare it to the dataset, returning the closest match.
"""

import face_recognition
import numpy as np
import glob
import os
import json
import math
from PIL import Image, ImageDraw
from flask import jsonify

DATASET = 'D:\Photography\CurrentProjects\Mugshot\mugshot\dataset\datasetjailbase.json'
# Below for use on droplet
# DATASET = '/root/Mugshot/dataset/datasetjailbase.json'
THRESHOLD = 0.6

def distance_to_percentage(face_distance, face_match_threshold=0.6):
    """
    Converts the distance result to a percentage value.

    :param face_distance: Distance result
    :param face_match_threshold: Strictness threshold. Lower values are stricter.

    :return: A percentage as float between 0.0 and 1.0
    """
    if face_distance > face_match_threshold:
        range = (1.0 - face_match_threshold)
        linear_val = (1.0 - face_distance) / (range * 2.0)
        return linear_val
    else:
        range = face_match_threshold
        linear_val = 1.0 - (face_distance / (range * 2.0))
        return linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))

def get_image_landmarks(img_file):
    image = face_recognition.load_image_file(img_file)

    landmarks_list = face_recognition.face_landmarks(image)

    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)

    for landmarks in landmarks_list:
        for facial_feature in landmarks.keys():
            draw.line(landmarks[facial_feature], fill=(0, 255, 0), width=10)

    return pil_image

def find_faces(img_file):
    """
    Takes in an image file and finds the location and encoding of faces in image

    :param img_file: Image file location as string

    :return: Returns a list of dicts, each containing face location and encoding
    """
    image = face_recognition.load_image_file(img_file)    
    faces_loc = face_recognition.face_locations(image)
    faces_enc = np.array(face_recognition.face_encodings(image, faces_loc))
    # TODO: faces_enc returns a list of ndarrays but once an index is called, the ndarray changes to a list
    results = []
    if len(faces_loc) == len(faces_enc): # Check if the length of faces_loc is the same as faces_enc
        for loc, enc in zip(faces_loc, faces_enc):
            list_entry = {"face_location": loc,
                          "face_encoding": enc}
            results.append(list_entry)

    return results

def find_closest_match(face_enc, dataset):
    """
    Compares an image file to a dataset and returns the closest match.

    :param img_file: Image file location as string
    :param dataset: Dataset containing encodings to compare image with

    :return: Returns the distance of the closest match and its charges
    """
    # Open the dataset file and load the data
    with open(dataset, "r") as read_file:
        data = json.load(read_file)

    # Print amount of entries (Pure debug info)
    # print("There are " + str(len(data['mugshots'])) + " entries in the dataset")

    y = 1
    distances = []
    charges = []

    for entry in data['mugshots']:
        # print("Checking image " + str(y) + " out of " + str(len(data['mugshots'])))
        enc_entry = [np.array(entry['encoding'])]

        distances.append(face_recognition.face_distance(enc_entry, face_enc))
        charges.append(entry['charges'])
        y += 1

    closest_match_distance = min(distances)
    charges = charges[distances.index(min(distances))]

    return closest_match_distance, charges



def match_image(img_file, return_json=False):
    """
    Compares an image file to a dataset and returns the closest match. A composite function of find_closest_match() and distance_to_percentage()

    :param img_file: Image file location as string

    :return: Returns list of dicts that each contain the distance of the closest match, its percentage and its charges
    """
    faces_list = find_faces(img_file)

    results = []
    for face in faces_list:
        face_distance, face_charges = find_closest_match(face["face_encoding"], DATASET)
        face_percentage = distance_to_percentage(face_distance, THRESHOLD)[0]

        results.append({
            "distance": face_distance[0],
            "percentage": face_percentage,
            "charges": face_charges
        })

    if return_json == False:
        return results
    else:
        return jsonify(results) #TODO: jsonifying the results does not work
        # return "Returned!"

print("Mugshot.py loaded!")