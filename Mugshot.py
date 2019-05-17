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

DATASET = 'mugshot\dataset\datasetjailbase.json'
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

def find_closest_match(img_file, dataset):
    """
    Compares an image file to a dataset and returns the closest match.
    :TODO: Rather than returning the distance and charges, should return the index

    :param img_file: Image file location as string
    :param dataset: Dataset containing encodings to compare image with

    :return: Returns the distance of the closest match and its charges
    """
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

    closest_match_distance = min(distances)
    charges = charges[distances.index(min(distances))]

    return closest_match_distance, charges

def get_image_landmarks(img_file):
    image = face_recognition.load_image_file(img_file)

    landmarks_list = face_recognition.face_landmarks(image)

    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)

    for landmarks in landmarks_list:
        for facial_feature in landmarks.keys():
            draw.line(landmarks[facial_feature], fill=(0, 255, 0), width=20)

    return pil_image


def match_image(img_file, return_json=False):
    """
    Compares an image file to a dataset and returns the closest match. A composite function of find_closest_match() and distance_to_percentage()

    :param img_file: Image file location as string

    :return: Returns the distance of the closest match, its percentage and its charges
    """
    match_distance, match_charges = find_closest_match(img_file, DATASET)
    match_percentage = distance_to_percentage(match_distance, THRESHOLD)[0]

    print("Accuracy percentage for image with a threshold of " + str(THRESHOLD) + ":")
    print(match_percentage)
    print("The matching individual was charged with: ")
    for charge in match_charges:
        print(charge)

    if return_json == False:
        return match_distance, match_percentage, match_charges
    else:
        results = {
            "match_distance": match_distance[0],
            "match_percentage": match_percentage,
            "match_charges": match_charges
        }
        return jsonify(results)
        # return "Returned!"
