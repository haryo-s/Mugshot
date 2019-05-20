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
    html_list = "<ul class=\"mt-decrease10 pb3\" style=\"list-style-type:none;\">\n"

    for item in list:
        html_list += "<li class=\"pl1 f-80\">" + str(item) + "</li>\n"

    html_list += "</ul>"

    return html_list

def encode_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)

    img_io_base64 = base64.b64encode(img_io.getvalue())  

    return img_io_base64  

def results_to_html(percentage, charges, face_number):
    match_percentage = "{0:.2f}%".format(percentage * 100)
    # l1 = "<h2 class=\"f-100\">Face #" + str(face_number) + "'s accuracy with its matching result was: </h2>\n" \
    #      "<p>" + match_percentage + "</p>\n" \
    #      "<h2 class=\"f-100\">The matching individual was charged with: </h2>\n" \
    #      "<p>" + charges + "</p>\n"

    l1 = "<h2 class=\"f-100\">Face #" + str(face_number) +  "</h2>\n" \
         "<h3 class=\"mt-decrease15 f-100\">Accuracy percentage with its matching result: </h3>\n" \
         "<p class=\"mt-decrease10 pl1\">" + match_percentage + "</p>\n" \
         "<h3 class=\"-100\">The matching individual was charged with: </h3>\n" \
         "<p>\n" + charges + "</p>\n"

    return l1

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
            i = 1

            if len(matched_faces) > 0:
                detection_results = "<h1 class=\"text-center\">One or more faces were detected!</h1>"
            else:
                detection_results = "<h1 class=\"text-center\">No faces were detected! Try another image.</h1>"
            for face in matched_faces:
                results_html_string += results_to_html(face['percentage'], python_list_to_html(face['charges']), i)
                i += 1

            return render_template('results.html',  detection_results = detection_results,
                                                    results = results_html_string,
                                                    landmarks = landmarks_img.decode('ascii'))

    # If no valid image file was uploaded, show the file upload form:
    return render_template('index.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)