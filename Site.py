from flask import Flask, jsonify, request, redirect, render_template, send_file
from PIL import Image
from io import BytesIO
from Mugshot import match_image, get_image_landmarks
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
from os import remove
import urllib.request
from urllib.parse import unquote
from functools import lru_cache
import hashlib
from resizeimage import resizeimage
from flask_cors import cross_origin

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

def urlDecode(url: str) -> str:
    return unquote(url)

@lru_cache(1000)
def strHash(string):
    # https://gist.github.com/nmalkin/e287f71788c57fd71bd0a7eec9345add
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def getImageFromNetwork(url: str) -> Image:
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)'
    }
    res = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
    img = Image.open(BytesIO(res.read()))
    return img

def imageResize(image, size):
    return resizeimage.resize_cover(image, size, validate=False)

def getImageFromMemcache(url, size) :
    # TODO: Make this LRU instead of infinitely growing
    global memcache

    urlHash = strHash(url)
    images = memcache.get(urlHash, None)
    if not images:
        print('Cache MISS for', url)
        try:
            original = getImageFromNetwork(url)
        except Exception as e:
            return getImageFromMemcache(BROKENIMAGE, size)
        memcache[urlHash] = {
            'original': original
        }
        if size:
            resized = imageResize(original, size)
            memcache[urlHash][size] = resized
            return resized
        else:
            return original

    desiredSize = images.get(size, None)
    if desiredSize:
        # print('Cache Hit!!')
        return desiredSize
    else:
        # print('Cache Hit!!')
        original = images.get('original', None)
        if size is None:
            return original
        return imageResize(original, size)


##############################
# FLASK/WEB SERVER FUNCTIONS #
##############################

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def serve_pil_image(pil_img):
    img_io = BytesIO()
    # pil_img.save(img_io, 'JPEG', quality=70)
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)

    return send_file(img_io, as_attachment=False, mimetype='image/jpeg')


@app.route('/', methods=['GET', 'POST'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
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
            landmarks_img = serve_pil_image(get_image_landmarks(file))
            # serve_img(file)

            match_distance, match_percentage, match_charges = match_image(file)
            match_charges = python_list_to_html(match_charges)

            # Convert the percentage float to a percentage
            match_percentage = "{0:.2f}%".format(match_percentage * 100)
            
            # return render_template('results.html',  percentage = match_percentage, 
            #                                         charges = match_charges)

            return landmarks_img

    # If no valid image file was uploaded, show the file upload form:
    return render_template('index.html')

# @app.route('/img')
# def serve_img():
#     img = Image.new('RGB', ...)
#     return serve_pil_image(get_image_landmarks(img))

@app.route('/fetch-image')
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def fetch_image():
    url = request.args.get('url')
    width = request.args.get('width', 'null')
    height = request.args.get('height', 'null')

    # print('Requested image-fetch', url, width, height)

    url = urlDecode(url)
    if width != 'null' and height != 'null':
        size = int(width), int(height)
    else:
        size = None

    image = getImageFromMemcache(url, size)
    # print(image)

    output = BytesIO()
    image.convert('RGBA').save(output, format='PNG')
    output.seek(0, 0)

    return send_file(output, mimetype='image/png', as_attachment=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)