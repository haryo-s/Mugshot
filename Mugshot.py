import face_recognition
import cv2
import numpy as np
import glob
import os
import logging
import json

IMAGES_PATH = './mugshot/images'
DATASET = './mugshot/dataset/dataset.json'
CAMERA_DEVICE_ID = 0
MAX_DISTANCE = 0.6


# for i, face_distance in enumerate(face_distances):
#     print("The test image has a distance of {:.4} from known image #{}".format(face_distance, i))
#     print("- With a normal cutoff of 0.6, would the test image match the known image? {}".format(face_distance < 0.6))
#     print("- With a very strict cutoff of 0.5, would the test image match the known image? {}".format(face_distance < 0.5))
#     print()

# def load_json(jsonfile):


# def load_json_entry():

personalimage = face_recognition.load_image_file('mugshot\dataset\images\personal\\jailbase1.jpg')
personal_loc = face_recognition.face_locations(personalimage)
personal_enc = face_recognition.face_encodings(personalimage, personal_loc)
print(str(len(personal_loc)) + " faces have been detected!")

with open(DATASET, "r") as read_file:
    data = json.load(read_file)

enc_nparray = np.array(data['mugshots'][2]['encoding'])

distances = []

print("There are " + str(len(data['mugshots'])) + " entries in the dataset")
y = 1

for x in data['mugshots']:
    
    print("Checking image " + str(y) + " out of " + str(len(data['mugshots'])))
    enc_x = np.array(x['encoding'])
    distances.append(face_recognition.face_distance(enc_x, personal_enc))
    y += 1

print(min(distances))
# distances = face_recognition.face_distance(enc_nparray, personal_enc)
# print(distances)

