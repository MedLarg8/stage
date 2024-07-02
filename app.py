from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify,Response
from flask_mysqldb import MySQL
from datetime import datetime
from empreinte_digitale import empreinte_functions
import base64
import hashlib
import os
import uuid  # for generating unique IDs
from werkzeug.utils import secure_filename
from deepface import DeepFace
import threading
import cv2
import functools

from project_functions import create_database_client, Client, check_imprint_validity, pass_transaction, get_client_by_username, Transaction, create_database_transaction

# OpenCV VideoCapture setup
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)  # Adjust the index or backend as needed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
face_match = False
recognition_started = False  # Flag to track if recognition is started

# Load reference image
reference_img = cv2.imread("reference.jpg")  # Update with your reference image path


UPLOAD_FOLDER = "static"

app = Flask(__name__)
app.secret_key = 'secret-key'

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'facial_recognition_table'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT image FROM user WHERE username = %s", [session['username']])
        user = cur.fetchone()
        cur.close()
        if user and user[0]:
            image = user[0]
        else:
            image = None
        return render_template('home.html', username=session['username'], image=image)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        bpassword = password.encode('utf-8')


        # Handle profile image upload
        if 'image' in request.files:
            image = request.files['image']

            if image.filename == '':
                image_filename = None
            else:
                # Generate a unique filename and create user folder
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
                os.makedirs(user_folder, exist_ok=True)  # Create user folder if it doesn't exist
                filename = str(uuid.uuid4()) + secure_filename(image.filename)
                image_path = os.path.join(user_folder, filename)
                image.save(image_path)
                image_filename = filename
        else:
            image_filename = None

        RegisteredClient = Client(username, bpassword, image_filename)
        clientCreated = create_database_client(RegisteredClient)

        if clientCreated:
            flash('You have successfully registered! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error in registration. Please try again.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE username = %s", [username])
        user = cur.fetchone()
        print("user : ",user)
        bpassword = password.encode('utf-8')
        bpassword = hashlib.sha1(bpassword).hexdigest()
        cur.close()
        if user and check_imprint_validity(username):  # user[2] is the password_hash column
            if bpassword==user[2]:
                session['username'] = user[1]  # user[1] is the username column
                return redirect(url_for('face_recognition'))
            else:
                print(user[2],"passed password is :",bpassword)
                print("invalid password hash")
        else:
            flash('Invalid user imprint, this user is not elligible to login. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/transaction', methods=['GET','POST'])
def transaction():
    print("transaction")
    if request.method == 'POST':
        print("post")
        sender_username = session['username']
        recepient_username = request.form['recipient']
        value = int(request.form['value'])
        print("sender username is : ",sender_username)
        print("recepient username is : ",recepient_username)
        sender = get_client_by_username(sender_username)
        print("SENDER :", sender)
        recepient = get_client_by_username(recepient_username)
        print("RECIEPIENT :",recepient)
        transaction = Transaction(sender, recepient,value)
        if create_database_transaction(transaction):
            print("TRANSACTION CREATED !!!!!!!!!!")
            pass_transaction(transaction)
        else:
            print("TRANSACTION NOT CREATED !!!!!!!!!")
        return redirect(url_for('transaction'))
    return render_template('transaction.html')


@app.route('/face_recognition', methods=['GET', 'POST'])
def face_recognition():
    if request.method == 'GET':
        return render_template('face_recognition.html')
    elif request.method == 'POST':
        # Process the image data received from client-side
        image_data = request.json.get('image', None)

        if image_data:
            # Decode base64 image data
            _, encoded_image = image_data.split(",", 1)
            decoded_image = base64.b64decode(encoded_image)

            # Save the image temporarily (optional for testing)
            temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.jpg')
            with open(temp_image_path, 'wb') as f:
                f.write(decoded_image)

            # Perform face recognition
            try:
                result = DeepFace.verify(temp_image_path, 'test.jpg')
                match = result['verified']
            except ValueError:
                match = False

            return jsonify({'match': match})

    return jsonify({'match': False})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

def check_face(frame, username):
    global face_match
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT image FROM user WHERE username = %s", [username])
            user_data = cur.fetchone()
            cur.close()

            if not user_data:
                print(f"No user found for username: {username}")
                face_match = False
                return

            image_fetch = user_data[0]
            if not image_fetch:
                print(f"No image found for user: {username}")
                face_match = False
                return

            image_path = os.path.join("static", username, image_fetch)
            image = cv2.imread(image_path)

            if image is None:
                print(f"Failed to read image from path: {image_path}")
                face_match = False
                return

            result = DeepFace.verify(frame, image)
            face_match = result['verified']
        except Exception as e:
            print(f"Error verifying face: {e}")
            face_match = False

def generate_frames(username):
    global face_match
    global counter
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if recognition_started and counter % 30 == 0:
            try:
                threading.Thread(target=functools.partial(check_face, frame.copy(), username)).start()
            except Exception as e:
                print(f"Error starting thread: {e}")

        counter += 1

        if face_match:
            cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/video_feed')
def video_feed():
    if 'username' in session:
        username = session['username']
        return Response(generate_frames(username), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return jsonify({'error': 'User not logged in'}), 403

@app.route('/start_recognition', methods=['GET'])
def start_recognition():
    global recognition_started
    if not recognition_started:
        recognition_started = True
        return jsonify({'message': 'Recognition started'})
    else:
        return jsonify({'message': 'Recognition already started'})

@app.route('/stop_recognition', methods=['GET'])
def stop_recognition():
    global recognition_started, face_match
    try:
        recognition_started = False
        if face_match:
            print("face match true")
            return redirect(url_for('transaction'))
        else:
            print("face match false")
            return jsonify({'message': 'Recognition stopped'})
    except Exception as e:
        print(f"Error in stop_recognition route: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
