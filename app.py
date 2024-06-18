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

UPLOAD_FOLDER = "C:/Users/MSI/Desktop/stage etc/static"


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
def index():
    return redirect(url_for('register'))

@app.route('/home')
def home():
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT profile_image FROM user WHERE username = %s", [session['username']])
        user = cur.fetchone()
        cur.close()
        if user and user[0]:
            profile_image = base64.b64encode(user[0]).decode('utf-8')
        else:
            profile_image = None
        return render_template('home.html', username=session['username'], profile_image=profile_image)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        h = hashlib.new('sha256')
        h.update(password.encode('utf-8'))
        password_hash = h.hexdigest()
        empreinte = empreinte_functions.create_empreinte(username, password_hash, datetime.now(), empreinte_functions.LIST_OF_ALGORITHMS)

        # Handle profile image upload
        if 'profile_image' in request.files:
            profile_image = request.files['profile_image']

            if profile_image.filename == '':
                profile_image_filename = None
            else:
                # Generate a unique filename
                filename = str(uuid.uuid4()) + secure_filename(profile_image.filename)
                profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_image_filename = filename
        else:
            profile_image_filename = None

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user (username, password, empreinte, image) VALUES (%s, %s, %s, %s)",
                    (username, password_hash, empreinte, profile_image_filename))
        mysql.connection.commit()
        cur.close()

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