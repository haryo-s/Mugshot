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

DATASET = './mugshot/dataset/dataset.json'
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

#'mugshot\dataset\images\personal\\tom.jpg'

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

    for x in data['mugshots']:
        # print("Checking image " + str(y) + " out of " + str(len(data['mugshots'])))
        enc_x = np.array(x['encoding'])
        distances.append(face_recognition.face_distance(enc_x, image_enc))
        y += 1

    closest_match = min(distances)

    return closest_match


tom = face_distance_to_conf(compare_face_to_dataset('mugshot\dataset\images\personal\\tom.jpg', DATASET)[0], THRESHOLD)
print("Accuracy percentage for Tom with a threshold of " + str(THRESHOLD) + ":")
print(tom)

print("")

haryo = face_distance_to_conf(compare_face_to_dataset('mugshot\dataset\images\personal\\haryo.jpg', DATASET)[0], THRESHOLD)
print("Accuracy percentage for Haryo with a threshold of " + str(THRESHOLD) + ":")
print(haryo)

