from blockChain.tuto import Client, Transaction, Block, mine, verify_signature, check_balance
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





def create_database_client(client):
    print("asserting instance")
    assert isinstance(client, Client) 
    username, password, image, date, empreinte, public_key, private_key, balance = client.username, client.password, client.image, client.date, client.empreinte, client._public_key, client._private_key, client._balance
    
    cur = mysql.connection.cursor()
    
    # Check if the username already exists
    
    cur.execute("SELECT 1 FROM user WHERE username = %s", (username,))
    
    result = cur.fetchone()
    
    
    if result:
        # Username already exists, do nothing
        print(f"User '{username}' already exists. No action taken.")
    else:
        # Insert the new client
        cur.execute("""INSERT INTO user (username, password, image, date, empreinte, `public-key`, `private-key`, balance) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (username, password, image, date, empreinte, public_key, private_key, balance))
        mysql.connection.commit()
        print(f"User '{username}' created successfully.")
    
    cur.close()



def create_database_transaction(transaction):#this function creates the transaction and updates the user table
    assert isinstance(transaction, Transaction)
    sender, recepient, value, time, signature = transaction.sender, transaction.recipient, transaction.value, transaction.time, transaction.signature
    sender_username = sender.username
    recepient_username = recepient.username
    if value<=sender._balance:

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO transactions(sender, recepient, value, time, signature) VALUES (%s,%s,%s,%s,%s)",
                    (sender, recepient, value, time, signature))
        
        cur.execute("UPDATE user SET balance = balance - %s WHERE username = %s",(value,sender_username))
        cur.execute("UPDATE user SET balance = balance + %s WHERE username = %s",(value,recepient_username))
        mysql.connection.commit()
    else:
        print("not enough balance")
    cur.close()

def get_verified_transactions_from_block(block_hash):
    pass

def create_database_block(block):
    assert isinstance(block,Block)

def pass_transaction(transaction):
    assert isinstance(transaction, Transaction)





if __name__ == "__main__":
    with app.app_context():
        #Dinesh = Client("dinesh",b"123456","image",900)
        #create_database_client(Dinesh)
        #Ramesh = Client("ramesh",b"123456","image",800)
        #create_database_client(Ramesh)
        #transaction1 = Transaction(Dinesh, Ramesh,100)
        #create_database_transaction(transaction1)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user")
        result = cur.fetchall()
        print(result[-1])

    

    