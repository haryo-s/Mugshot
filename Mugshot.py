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

DATASET = 'D:\Photography\CurrentProjects\Mugshot\mugshot\dataset\datasetjailbase.json'
THRESHOLD = 0.6

def face_distance_to_conf(face_distance, face_match_threshold=0.6):
    if face_distance > face_match_threshold:
        range = (1.0 - face_match_threshold)
        linear_val = (1.0 - face_distance) / (range * 2.0)
        return linear_val
    else:
        range = face_match_threshold
        linear_val = 1.0 - (face_distance / (range * 2.0))
        return linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))

def compare_face_to_dataset(img_file, dataset):
    image = face_recognition.load_image_file(img_file)
    image_loc = face_recognition.face_locations(image)
    image_enc = face_recognition.face_encodings(image, image_loc)
    print(str(len(image_loc)) + " faces have been detected!")

    with open(dataset, "r") as read_file:
        data = json.load(read_file)

    print("There are " + str(len(data['mugshots'])) + " entries in the dataset")

    y = 1
    distances = []
    charges = []

    for entry in data['mugshots']:
        # print("Checking image " + str(y) + " out of " + str(len(data['mugshots'])))
        enc_entry = np.array(entry['encoding'])

        distances.append(face_recognition.face_distance(enc_entry, image_enc))
        charges.append(entry['charges'])
        y += 1

    closest_match = min(distances)
    charges = charges[distances.index(min(distances))]

    return closest_match, charges

def get_image_closest_match(image_file):
    match, match_charges = compare_face_to_dataset(image_file, DATASET)
    match_percentage = face_distance_to_conf(match, THRESHOLD)[0]

    print("Accuracy percentage for image with a threshold of " + str(THRESHOLD) + ":")
    print(match_percentage)
    print("The matching individual was charged with: ")
    for charge in match_charges:
        print(charge)

    return match, match_percentage, match_charges

get_image_closest_match('D:\Photography\CurrentProjects\Mugshot\mugshot\dataset\images\personal\\tom.jpg')