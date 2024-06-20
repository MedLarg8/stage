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
    identity = client.identity
    cur = mysql.connection.cursor()
    
    # Check if the username already exists
    
    cur.execute("SELECT 1 FROM user WHERE username = %s", (username,))
    
    result = cur.fetchone()
    
    
    if result:
        # Username already exists, do nothing
        print(f"User '{username}' already exists. No action taken.")
    else:
        # Insert the new client
        cur.execute("""INSERT INTO user (username, password, image, date, empreinte, `public-key`, `private-key`, identity, balance) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (username, password, image, date, empreinte, public_key, private_key,identity, balance))
        mysql.connection.commit()
        print(f"User '{username}' created successfully.")
    
    cur.close()



def create_database_transaction(transaction):#this function creates the transaction and updates the user table
    assert isinstance(transaction, Transaction)
    sender_username = transaction.sender.username
    recepient_username = transaction.recipient.username
    sender = get_client_by_username(sender_username)
    recepient = get_client_by_username(recepient_username)
    value, time, signature = transaction.value, transaction.time, transaction.signature
    
    if value<=sender._balance:

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO transactions(sender, recepient, value, time, signature) VALUES (%s,%s,%s,%s,%s)",
                    (sender.aux_identity, recepient.aux_identity, value, time, signature))
        
        cur.execute("UPDATE user SET balance = balance - %s WHERE username = %s",(value,sender_username))
        cur.execute("UPDATE user SET balance = balance + %s WHERE username = %s",(value,recepient_username))
        mysql.connection.commit()
    else:
        print("not enough balance")
    cur.close()

def get_verified_transactions_from_last_block():
    cur = mysql.connection.cursor()
    cur.execute("SELECT verified_transactions from blockchain ORDER BY id DESC LIMIT 1")
    #turn result into a list
    result = cur.fetchone()
    return get_list_from_str(result)

def get_list_from_str(str):
    list_str = str.split(',')
    list_final = [int(num) for num in list_str]
    return list_final

def get_str_from_list(number_list):
    number_list_str = [str(num) for num in number_list]
    number_string = ",".join(number_list_str)
    return number_string



def create_database_block(digest=None):
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO blockchain (previous_block_hash) VALUES(%s)",
                (digest,))
    mysql.connection.commit()
    cur.close()


def can_pass_transaction(transaction):
    assert isinstance(transaction, Transaction)
    last_block = Block()
    cur = mysql.connection.cursor()
    cur.execute("SELECT verified_transactions FROM blockchain ORDER BY id DESC LIMIT 1")
    resultat = cur.fetchone()

    if resultat and resultat[0]:  # Check if resultat is not None and resultat[0] is not None
        verified_transactions_signatures = get_list_from_str(resultat[0])
    else:
        verified_transactions_signatures = []

    list_transaction = []
    for i in verified_transactions_signatures:
        temp_transaction = Transaction()
        cur.execute("SELECT * FROM transactions WHERE signature = %s", (i,))
        resultat = cur.fetchone()
        temp_transaction.sender = resultat[1]
        temp_transaction.recipient = resultat[2]
        temp_transaction.value = resultat[3]
        temp_transaction.time = resultat[4]
        temp_transaction.signature = resultat[5]
        list_transaction.append(temp_transaction)

    last_block.verified_transaction = list_transaction
    return last_block.can_add_transaction(transaction)

    
def create_nonce_for_last_block():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from blockchain ORDER BY id DESC LIMIT 1")
    resultat = cur.fetchone()
    verified_transactions = resultat[1]
    previous_block_hash = resultat[2]
    block = Block()
    block.verified_transaction = verified_transactions
    block.previous_block_hash = previous_block_hash
    block.Nonce = mine(block,2)
    digest = hash(block)
    cur.execute("SELECT MAX(id) FROM blockchain")
    max_id = cur.fetchone()[0]  

    cur.execute("UPDATE blockchain SET nonce = %s WHERE id = %s",
                (block.Nonce, max_id))
    mysql.connection.commit()
    cur.close()
    return digest





def add_transaction_to_last_block(transaction):
    assert isinstance(transaction, Transaction)
    cur = mysql.connection.cursor()

    cur.execute("SELECT MAX(id) FROM blockchain")
    max_id = cur.fetchone()[0]  
    
    cur.execute("SELECT verified_transactions from blockchain WHERE id = %s",
                (max_id,))
    resultat = cur.fetchone()
    print("max id : ",max_id)
    print("signature : ")
    print(transaction.signature)
    
    if resultat != None:

        cur.execute("UPDATE blockchain SET verified_transactions = verified_transactions +','+ %s WHERE id = %s",
                    (transaction.signature, max_id))
    else:
        cur.execute("UPDATE blockchain SET verified_transactions =  %s WHERE id = %s",
                    (transaction.signature, max_id))
        
    mysql.connection.commit()

    cur.close()

def is_blockchain_empty():
    cur=mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) from blockchain")
    resultat = cur.fetchone()[0]

    if resultat > 0:
        return False
    return True


def pass_transaction(transaction):
    assert isinstance(transaction,Transaction)
    if is_blockchain_empty():
        create_database_block()
    else:
        if can_pass_transaction(transaction):
            add_transaction_to_last_block(transaction)
        else:
            digest = create_nonce_for_last_block()
            create_database_block(digest)
            add_transaction_to_last_block(transaction)




def get_client_by_username(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE username = %s",
                                  (username,))
    resultat = cur.fetchone()
    print("resultat is :",resultat)
    password = resultat[2]
    image = resultat[3]
    date = resultat[4]
    empreinte = resultat[5]
    public_key = resultat[6]
    private_key = resultat[7]
    aux_identity = resultat[8]
    balance = resultat[9]
    password = password.encode('utf-8')
    client = Client(username,password,image,balance)
    client._private_key = private_key
    client._public_key = public_key
    client.date = date
    client.empreinte = empreinte
    client.aux_identity = aux_identity
    return client
    



if __name__ == "__main__":
    with app.app_context():
        Dinesh = Client("dinesh",b"123456","image",900)
        create_database_client(Dinesh)
        Ramesh = Client("ramesh",b"123456","image",800)
        create_database_client(Ramesh)
        transaction1 = Transaction(Dinesh, Ramesh,100)
        create_database_transaction(transaction1)
        print("transaction created")
        pass_transaction(transaction1)

    

    