# MUGSHOT

# This script will take in an image and compare it to the dataset, returning the closest match.

import face_recognition
import numpy as np
import glob
import os
import json
import math
from flask import Flask, jsonify, request, redirect, render_template

DATASET = 'D:\Photography\CurrentProjects\Mugshot\mugshot\dataset\datasetjailbase.json'
THRESHOLD = 0.6
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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

########################################

def python_list_to_html(list):
    html_list = "<ul>\n"

    for item in list:
        html_list += "<li>" + str(item) + "</li>\n"

    html_list += "</ul>"

    return html_list

########################################

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            match_distance, match_percentage, match_charges = match_image(file)
            match_charges = python_list_to_html(match_charges)
            
            return render_template('results.html',  percentage = match_percentage, 
                                                    charges = match_charges)

    # If no valid image file was uploaded, show the file upload form:
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)