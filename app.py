from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from empreinte_digitale import empreinte_functions 
import base64
import hashlib
import os
import uuid  # for generating unique IDs
from werkzeug.utils import secure_filename
from project_functions import create_database_client, Client

UPLOAD_FOLDER = "static"


app = Flask(__name__)
app.secret_key = 'secret-key'
#testing commit
# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'stage_facial_recognition'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    


mysql = MySQL(app)

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/home')
def home():
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT image FROM user WHERE username = %s", [session['username']])
        user = cur.fetchone()
        cur.close()
        if user and user[0]:
            image = base64.b64encode(user[0]).decode('utf-8')
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
        image = request.form['image']
        RegisteredClient = Client(username,bpassword,image)
        clientCreated = create_database_client(RegisteredClient)

        if clientCreated:
            pass
            #create folder for user by his username in static(UPLOAD_FOLDER) 
            #save the image passed in that folder and create a unique id for it
        else:
            pass

        # Handle profile image upload
        if 'image' in request.files:
            image = request.files['image']

            if image.filename == '':
                image_filename = None
            else:
                # Generate a unique filename
                filename = str(uuid.uuid4()) + secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        else:
            image_filename = None


        flash('You have successfully registered! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE username = %s", [username])
        user = cur.fetchone()
        cur.close()
        #add check empreinte function here
        if user and check_password_hash(user[2], password):  # user[2] is the password_hash column
            session['username'] = user[1]  # user[1] is the username column
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)