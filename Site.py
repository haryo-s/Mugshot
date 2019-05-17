from flask import Flask, jsonify, request, redirect, render_template, send_file
from PIL import Image
from io import BytesIO
from Mugshot import match_image, get_image_landmarks
import base64

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
BROKENIMAGE = ""
memcache = {}

#######################
# AUXILIARY FUNCTIONS #
#######################

def python_list_to_html(list):
    html_list = "<ul>\n"

    for item in list:
        html_list += "<li>" + str(item) + "</li>\n"

    html_list += "</ul>"

    return html_list

def encode_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)

    img_io_base64 = base64.b64encode(img_io.getvalue())  

    return img_io_base64  

##############################
# FLASK/WEB SERVER FUNCTIONS #
##############################

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
            landmarks_img = encode_image(get_image_landmarks(file))

            match_distance, match_percentage, match_charges = match_image(file)
            match_charges = python_list_to_html(match_charges)

            # Convert the percentage float to a percentage
            match_percentage = "{0:.2f}%".format(match_percentage * 100)
            
            return render_template('results.html',  percentage = match_percentage, 
                                                    charges = match_charges,
                                                    landmarks = landmarks_img.decode('ascii'))

    # If no valid image file was uploaded, show the file upload form:
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)