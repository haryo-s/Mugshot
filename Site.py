from flask import Flask, jsonify, request, redirect, render_template, send_file
from PIL import Image
from io import BytesIO
import Mugshot
import base64

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
BROKENIMAGE = ""

#######################
# AUXILIARY FUNCTIONS #
#######################

def python_list_to_html(list):
    """
    Converts a Python list object to a formatted HTML list string

    :param list: Python list object

    :return: Formatted html list string
    """
    html_list = "<ul class=\"mt-decrease10\" style=\"list-style-type:none;\">\n"

    for item in list:
        html_list += "<li class=\"pl1\">" + str(item) + "</li>\n"

    html_list += "</ul>"

    return html_list

def encode_image(pil_img):
    """
    Encodes a PIL image object to a base64 bytes object

    :param pil_img: PIL image object

    :return: An JPEG image encoded in base64 bytes
    """
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)

    img_io_base64 = base64.b64encode(img_io.getvalue())  

    return img_io_base64  

def results_to_html(distance, charges, face_number):
    """
    Creates a formatted html string to display the results of each analyzed face

    :param percentage: Float between 0.0 and 1.0 representing the percentage
    :param charges: Formatted html list string of the charges (created by python_list_to_html())
    :param face_number: Integer of the number of face

    :return: Formatted html string of the results
    """
    percentage = Mugshot.distance_to_percentage(distance)
    match_percentage = "{0:.2f}%".format(percentage * 100)

    if percentage > 0.75:
        match_string = "You would be considered a possible match with a threshold of 0.5."
    else:
        match_string = "You would not be considered a match."

    results = "<div class=\"results mb-1\"\n>" \
              "<h2 class=\"mt-decrease f-100\">Face #" + str(face_number) +  "</h2>\n" \
              "<h4 class=\"mt-decrease15 f-100\">Image's accuracy percentage with its closest matching result:</h4>\n" \
              "<p class=\"mt-decrease15 pl1\">" + match_percentage + "</p>\n" \
              "<h4 class=\"f-100\">" + match_string + "</h4>\n" \
              "<h4 class=\"-100\">The matching individual was charged with: </h4>\n" \
              "<p class=\"mt-decrease15\">\n" + charges + "</p>\n" \
              "</div>"

    return results

##############################
# FLASK/WEB SERVER FUNCTIONS #
##############################

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def results_page():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            landmarks_img = encode_image(Mugshot.draw_image_landmarks(file, square=True, outline=True))

            matched_faces = Mugshot.match_image(file)
            results_html_string = ""
            i = 1

            if len(matched_faces) > 0:
                detection_results = "<h1 class=\"text-center\">One or more faces were detected!</h1>"
            else:
                detection_results = "<h1 class=\"text-center\">No faces were detected! Try another image.</h1>"

            for face in matched_faces:
                results_html_string += results_to_html(face['distance'], python_list_to_html(face['charges']), i)
                i += 1

            return render_template('results.html',  detection_results = detection_results,
                                                    results = results_html_string,
                                                    landmarks = landmarks_img.decode('ascii'))

    # If no valid image file was uploaded, show the file upload form:
    return redirect('/')

@app.route('/about')
def about_page():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)