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
# DATASET = '/home/haryo/Mugshot/Mugshot/dataset/datasetjailbase.json'
THRESHOLD = 0.5

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

def get_amount_entries(dataset):
    """
    Gets the amount of entries

    :param dataset: Dataset to analyze

    :return: Returns the amount of entries in dataset as int
    """
    with open(dataset, "r") as read_file:
        data = json.load(read_file)

    return len(data['mugshots'])

def find_faces(img_file):
    """
    Takes in an image file and finds the location and encoding of faces in image

    :param img_file: Image file location as string

    :return: Returns a list of dicts, each containing face_location and face_encoding
    """
    image = face_recognition.load_image_file(img_file)
    faces_loc = face_recognition.face_locations(image)
    faces_landmarks = face_recognition.face_landmarks(image)
    faces_enc = np.array(face_recognition.face_encodings(image, faces_loc))
    # TODO: faces_enc returns a list of ndarrays but once an index is called, the ndarray changes to a list
    results = []
    if len(faces_loc) == len(faces_enc):
        for loc, enc, landmarks in zip(faces_loc, faces_enc, faces_landmarks):
            list_entry = {"face_location": loc,
                          "face_encoding": enc,
                          "face_landmarks": landmarks}
            results.append(list_entry)

    return results

def draw_image_landmarks(img_file, faces=None, line_color=(0, 255, 0), line_width_multiplier=1, square=True, outline=False, points=False):
    """
    Draw the facial landmarks of each face in the image
    TODO: Change arguments to accept face_locations and landmarks, so that the face recognition segment is done only once for each image

    :param img_file: Image file location as string
    :param faces: List of dicts containing face_location and face_encoding, as returned by find_faces(). If not included it will use the img_file to get required data.
    :param line_color: Color of the drawn lines
    :param line_width_multiplier: Multiplies the width of the drawn lines. Line width is 1/100 of image height.
    :param square: Draw square around face 
    :param outline: Draw face outline around face 
    :param points: Draw points on face  

    :return: PIL Image object on which the landmarks are drawn
    """
    if faces != None:
        image = face_recognition.load_image_file(img_file)
        pil_image = Image.fromarray(image)
        lines_list = face_recognition.face_locations(image)
        landmarks_list = face_recognition.face_landmarks(image)

    else:
        image = face_recognition.load_image_file(img_file)
        pil_image = Image.fromarray(image)
        lines_list = [face['face_location'] for face in faces]
        landmarks_list = [face['face_encoding'] for face in faces]

    height, width = pil_image.size
    line_width = int(height/100) * line_width_multiplier

    # Draw lines on the image
    draw = ImageDraw.Draw(pil_image)

    if outline == True:
        for (top, right, bottom, left) in lines_list:
            draw.rectangle(((left, top), (right, bottom)), outline=line_color, width=line_width)

    if square == True:
        for landmark in landmarks_list:
            for facial_feature in landmark.keys():
                draw.line(landmark[facial_feature], fill=line_color, width=line_width)

    # Resize the resulting image if it is wider than 600px
    if pil_image.width > 600:
        pil_image_h = int(pil_image.height * (600 / pil_image.width))
        pil_image_w = 600
        pil_image = pil_image.resize((pil_image_w, pil_image_h))

    return pil_image

def crop_faces(img_file):
    """
    Takes in an image file and creates a crop of each face it finds.

    TODO: Create crop_faces function
    """
    faces = find_faces(img_file)

    image = face_recognition.load_image_file(img_file)
    pil_image = Image.fromarray(image)

    cropped_faces = []
    for face in faces:
        faces[face]["face_location"]
        cropped_image = pil_image.crop(faces[face]["face_location"])

        cropped_faces.append(cropped_image)

    return cropped_faces

def find_closest_match(face_enc, dataset):
    """
    Compares an image file to a dataset and returns the closest match.

    :param face_enc: The unique encoding of a face as a 128-dimensional list
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

if __name__ == "__main__":
    print("Mugshot.py loaded!")
    print(str(get_amount_entries(DATASET)))
