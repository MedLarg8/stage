from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import face_recognition
import face_recognition_models
#from face_recognition_functions import get_face_names, check_name, start_recognition
import uuid
import os




UPLOAD_FOLDER = "C:/Users/MSI/Desktop/stage/facial-recognition/usersImages"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.secret_key = 'secret-key'
#testing commit
# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'stage_facial_regonition'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

@app.route('/')
def home():
    print("Entering home route")
    if 'username' in session:  # Corrected the session key name
        return render_template('home.html', username=session['username'])
    else:
        return render_template('home.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        pwd = request.form.get('password')
        cur = mysql.connection.cursor()
        cur.execute(f"select username, password from user where username = '{username}'")
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[2]:
            session['username'] = user
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('password')
        image = request.files['image']

        imageId = uuid.uuid4()

        mode = 0o666
        image_path = os.path.join(UPLOAD_FOLDER, username)
        
        #checking if path exists
        if not os.path.exists(image_path):
            os.mkdir(image_path, mode)

        #checking if user passed an image
        uploadImage(image, username)
        
        # Add code to insert the new user into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, pwd))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    else:
        return render_template('register.html')
    

def uploadImage(image, username):
    if image and allowed_file(image.filename):
        imageName = secure_filename(image.filename)
        imagePath = os.path.join(UPLOAD_FOLDER, username)
        if os.path.exists(imagePath)==False:
            os.mkdir(imagePath)
        
        image.save(os.path.join(imagePath, imageName))
        print("Image saved")
    else:
        print("Image's name is not allowed (allowed extensions)")                 

                
    
    




def allowed_file(filename):     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Ensure Flask app runs
if __name__ == "__main__":
    app.run(debug=True)