from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from empreinte_digitale import empreinte_functions
import base64
import hashlib
import os
import uuid  # for generating unique IDs
from werkzeug.utils import secure_filename
from deepface import DeepFace

from project_functions import create_database_client, Client, check_imprint_validity, pass_transaction, get_client_by_username, Transaction, create_database_transaction

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
                return redirect(url_for('transaction'))
            else:
                print(user[2],"passed password is :",bpassword)
                print("invalid password hash")
        else:
            flash('Invalid username or password. Please try again.', 'danger')
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

if __name__ == '__main__':
    app.run(debug=True)
