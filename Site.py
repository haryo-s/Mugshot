from flask import Flask, jsonify, request, redirect, render_template, send_file
from PIL import Image
from io import BytesIO
import Mugshot
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

def results_to_html(percentage, charges):
    l1 = "<h2>This face's accuracy percentage with matching result was: </h2>\n"
    l2 = "<h3>" + str(percentage) + "</h3>\n"

    l3 = "<h2>The matching individual was charged with: </h2>\n"
    l4 = "<h3>" + charges + "</h3>\n"

    return l1 + l2 + l3+ l4

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
            landmarks_img = encode_image(Mugshot.get_image_landmarks(file))

            matched_faces = Mugshot.match_image(file)
            results_html_string = ""
            for face in matched_faces:
                results_html_string += results_to_html(face['percentage'], python_list_to_html(face['charges']))

            return render_template('results.html',  results = results_html_string,
                                                    landmarks = landmarks_img.decode('ascii'))

    # If no valid image file was uploaded, show the file upload form:
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)