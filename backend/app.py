from flask import Flask, jsonify, request, render_template, session, send_file, redirect
from flask_cors import CORS
from datetime import timedelta
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv(override=True)

from database import authenticate_user_with_db, add_user, delete_user, get_user_statistics, check_owner_match
from database import insert_image, get_list_offset, delete_image, find_image
from database import get_album_list, create_album, delete_album, add_image_to_album, del_image_from_album
from image import generate_thumbnails, scrape_metadata
from storage import storage

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET')
app.permanent_session_lifetime = timedelta(days=14)

app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

CORS(app, origins=r"^http://.*$", supports_credentials=True)

# User Mgmt + Dashboard (SSR)

@app.route('/', methods=['GET'])
def hello_world():
    if 'superuser' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/superuser', methods=['POST'])
def superuser_check():
    if request.method == 'POST':
        form_data = request.form
        if form_data.get('password') == os.getenv('MASTER_KEY'):
            session['superuser'] = 'true'
            return redirect('dashboard')
        else:
            return render_template('error.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'superuser' in session: 
        return render_template('dashboard.html', user_data=get_user_statistics())
    else: 
        return render_template('error.html')

@app.route('/users/add', methods=['POST'])
def create_new_user():
    if 'superuser' in session:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            add_user(username, password)
            return redirect('../dashboard')
    else:
        return render_template('error.html')

@app.route('/users/delete', methods=['POST'])
def delete_existing_user():
    if 'superuser' in session:
        if request.method == "POST":
            form_data = request.form
            for users in form_data.keys():
                delete_user(users)
            return redirect('../dashboard')
    else:
        return render_template('error.html')
        
# Main App User Handling & Authentication (REST)

def authenticate_user(passed_function):
    @wraps(passed_function)
    def check_user(*args, **kwargs):
        if 'user_id' in session:
            return passed_function(*args, **kwargs)
        else:
            return jsonify({'status': 'unauthenticated'}), 401
        
    return check_user

@app.route('/api/user', methods=['POST'])
def logged_user():
    if 'user_id' in session:
        return jsonify({'status': 'authenticated', 'username':session.get('user_id')}), 200
    else:
        return jsonify({'status': 'unauthenticated', 'username': 'none'}), 401


@app.route('/api/authenticate', methods=['POST'])
def auth_user():
    session.permanent = True
    credentials = request.get_json()
    if authenticate_user_with_db(credentials.get('username'), credentials.get('password')):
        session['user_id'] = credentials.get('username')
        return jsonify({'status': 'authenticated'}), 200
    else: 
        return jsonify({'status': 'unauthenticated'}), 401

@app.route('/api/logout', methods=['POST'])
def logout_user():
    session.clear()
    return jsonify({'status': 'unauthenticated'}), 200

# Image Uploads and Downloads

@app.route('/api/upload', methods=['POST'])
@authenticate_user
def upload():

    if request.method == 'POST':
       
        files = request.files.getlist('file_upload')

        if len(files) == 0: 
            return jsonify({'status': 'failed', 'message': 'No Files Uploaded'}), 400

        for file in files:

            filename = file.filename
            file_ext = os.path.splitext(filename)[1]
            file_data = file.read()
            
            image_metadata = scrape_metadata(file_data, filename)
            file_hash = image_metadata['img_id'].hex()
            thumbnail_data = generate_thumbnails(file_data)

            storage.upload(file_hash, file_ext, file_data)
            storage.upload_thumbnail(file_hash, thumbnail_data)

            insert_image(**image_metadata, username=session.get('user_id'))

    return jsonify({'status': 'success'}), 200

@app.route('/api/thumbnail/<string:alb_id>/<int:offset_num>', methods=['POST'])
@authenticate_user
def send_thumbnail_list(alb_id, offset_num):
    image_data = get_list_offset(session.get('user_id'), offset_num, album_id=alb_id)
    data_array = []
    for images in image_data:
        data_frame = {'ImageId':images.ImageId.hex(), 'DateTaken':images.DateTaken.isoformat()}
        data_array.append(data_frame)
    if len(data_array) == 0:
        return jsonify({"hasMore": False, "imageHashes": []})
    return jsonify({"hasMore": True, "imageHashes": data_array})

@app.route('/api/thumbnail/download/<string:image_id>', methods=['GET'])
@authenticate_user
def download_thumb(image_id):
    try:
        is_owner = check_owner_match(session.get('user_id'), bytes.fromhex(image_id))
        if is_owner == True:
            image_binary_data = storage.download_thumb(image_id)
            image_binary_data.seek(0)
            return send_file(image_binary_data, mimetype='image/webp', download_name=f'{image_id}.webp')
        else:
            return jsonify({'status': 'unauthorized'}), 401
    except:
        return "Unable to find image file", 500

@app.route('/api/image/download/<string:image_id>', methods=['GET'])
@authenticate_user
def download_image(image_id):
    try:
        image_name = find_image(session.get('user_id'), bytes.fromhex(image_id))[1]
        image_ext = os.path.splitext(image_name)[1]
        image_binary_data = storage.download(image_id, image_ext)
        image_binary_data.seek(0)
        return send_file(image_binary_data, download_name=f'{image_name}')
    except:
        return "Unable to find image file", 500

@app.route('/api/image/info/<string:image_id>', methods=['GET'])
def get_image_data(image_id):
    try:
        image_data = find_image(session.get('user_id'), bytes.fromhex(image_id))
        image_json = {
            'ImageId': image_data[0],
            'ImageName': image_data[1],
            'ImageXRes': image_data[2],
            'ImageYRes': image_data[3],
            'ImageDateTaken': image_data[4].isoformat()
        }
        return jsonify(image_json), 200
    except:
        return "Unable to find image file", 500

@app.route('/api/delete/<string:image_id>', methods=['POST'])
@authenticate_user
def delete(image_id):
    is_nolonger_exist = delete_image(session.get('user_id'), bytes.fromhex(image_id))
    print(is_nolonger_exist)
    if is_nolonger_exist:
        storage.delete_func(image_id)
        return jsonify({'status': 'success', 'isDeleted': True}), 200
    else:
        return jsonify({'status': 'success', 'isDeleted': False}), 200
    
# Album Operations

@app.route('/api/albums/list', methods=['GET'])
@authenticate_user
def album_list_response():

    list_of_albums = get_album_list(session.get('user_id'))
    returned_album = {}

    for albums in list_of_albums:
        returned_album[albums.AlbumName] = albums.AlbumId

    return jsonify(returned_album)

@app.route('/api/albums/create', methods=['POST'])
@authenticate_user
def creating_the_album():
    if request.method == 'POST':
        json_data = request.get_json()
        create_album(session.get('user_id'), json_data.get('album_name'))
        return jsonify({'status': 'success'}), 200

@app.route('/api/albums/delete', methods=['POST'])
@authenticate_user
def deleting_the_album():
    if request.method == 'POST':
        json_data = request.get_json()
        delete_album(session.get('user_id'), json_data.get('album_id'))
        return jsonify({'status': 'success'}), 200

@app.route('/api/albums/move', methods=['POST'])
@authenticate_user
def moving_image_to_album():
    if request.method == 'POST':
        json_data = request.get_json()
        add_image_to_album(session.get('user_id'), bytes.fromhex(json_data.get('image_id')), json_data.get('album_id'))
        return jsonify({'status': 'success'}), 200

@app.route('/api/albums/remove', methods=['POST'])
@authenticate_user
def deleting_image_from_album():
    if request.method == 'POST':
        json_data = request.get_json()
        del_image_from_album(session.get('user_id'), bytes.fromhex(json_data.get('image_id')), json_data.get('album_id'))
        return jsonify({'status': 'success'}), 200

if __name__ == "__main__":
    app.run(debug=True, threaded=True)