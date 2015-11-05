import os
import os.path
import hashlib
import requests
import json
from flask import Flask, request, redirect, \
    url_for, jsonify, send_from_directory
from flask.ext.cors import CORS
from flask.ext.compress import Compress
from werkzeug import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_IMAGES'] = 255
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/xml',
                                    'application/json',
                                    'application/javascript',
                                    'image/jpeg', 'image/png']

# Helper methods
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def hash_name(filename):
    md5 = hashlib.md5()
    md5.update(filename)
    return str(md5.hexdigest()) + '.jpg'


def purge():
    # list of files in upload folder by last modified time
    folder = sorted(os.listdir(UPLOAD_FOLDER), key=lambda x: os.path.getmtime(
        os.path.join(UPLOAD_FOLDER, x)))
    curr_num_files = len(
        [name for name in folder
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, name))])

    if(curr_num_files > app.config['MAX_IMAGES']):
        for name in folder[0:100]:
            path = os.path.join(UPLOAD_FOLDER, name)
            try:
                if os.path.isfile(path):
                    os.unlink(path)
            except Exception, e:
                print e

# Routes


@app.route('/upload/file', methods=['POST'])
def upload_file():
    purge()

    if request.method == 'POST':
        file = request.files['file']

        if not file or not allowed_file(file.filename):
            return json.dumps({'success': False,
                               'error': 'Not a valid image file'})

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_url = url_for('get_image', filename=filename, _external=True)

        success_response = {
            'success': 'true',
            'new_url': new_url
        }

        return jsonify(success_response)

@app.route('/upload/url', methods=['POST'])
def upload_file_by_url():
    purge()

    if request.method == 'POST':
        url = request.form['url'].strip()

        r = None
        error = False

        try:
            r = requests.get(url)
        except requests.ConnectionError:
            # failed to make connection to URL
            error = True

        # if can't get file at URL
        if error or r.status_code != 200:
            return json.dumps({'success': False, 'error': 'Not a valid URL'})

        filename = hash_name(url)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # write image to file
        with open(filepath, 'wb') as fd:
            for chunk in r.iter_content(2**5):
                fd.write(chunk)

        success_response = {
            'success': 'true',
            'new_url': url_for('get_image', filename=filename, _external=True)
        }

        return jsonify(success_response)


@app.route('/get/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory('uploads', filename)


if __name__ == '__main__':
    CORS(app)
    Compress(app)
    app.debug = True
    app.run(host='0.0.0.0')
