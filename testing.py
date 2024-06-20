from blockChain.tuto import Client, ClientInfo, Transaction
from flask import Flask
from flask_mysqldb import MySQL
import datetime

UPLOAD_FOLDER = "static"

app = Flask(__name__)
app.secret_key = 'secret-key'
#testing commit
# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'facial_recognition_table'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)





def create_Database_Transaction(transaction):
    assert isinstance(transaction,Transaction)
    sender = transaction.sender
    recepient = transaction.recepient
    value = transaction.value
    date = transaction.date
    signature = transaction.signature
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO transactions (sender,recepient,value,date,signature) VALUES(%s,%s,%i,%d,%s)",
                (sender,recepient,value,date,signature))
    

def create_database_client(client,client_info):
    assert isinstance(client,Client) 
    assert isinstance(client_info, ClientInfo)
    username, password, image, date, empreinte, public_key, private_key, balance  = client_info.username, client_info.password, client_info.image, client_info.date, client_info.empreinte, client._public_key, client._private_key, client._balance
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user (username, password,image, date, empreinte, `public-key`, `private-key`, balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (username, password, image, date, empreinte, public_key, private_key, balance))
    mysql.connection.commit()
    cur.close()



if __name__ == "__main__":
    with app.app_context():
        Med = Client(5000)
        Med_info = ClientInfo("mohamed", b"123456", "image")
        print("************")
        create_database_client(Med, Med_info)
        print("************")