from blockChain.tuto import Client, ClientInfo, Transaction, Block, mine, verify_signature, check_balance
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
    mysql.connection.commit()
    cur.close()
    

def create_database_client(client,client_info):
    assert isinstance(client,Client) 
    assert isinstance(client_info, ClientInfo)
    username, password, image, date, empreinte, public_key, private_key, balance  = client_info.username, client_info.password, client_info.image, client_info.date, client_info.empreinte, client._public_key, client._private_key, client._balance
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user (username, password,image, date, empreinte, `public-key`, `private-key`, balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (username, password, image, date, empreinte, public_key, private_key, balance))
    mysql.connection.commit()
    cur.close()


def execute_transaction(transaction):
    assert isinstance(transaction, Transaction)

    sender = transaction.sender
    recepient = transaction.recipient
    value = transaction.value

    


def pass_transaction(transactions):
    global LAST_BLOCK_HASH
    global LAST_TRANSACTION_INDEX
    global ALL_TRANSACTIONS
    print("LAST BLOCK HASH : ",LAST_BLOCK_HASH)
    print("LAST TRANSACTION INDEX : ",LAST_TRANSACTION_INDEX)
    if not transactions:
        return
    else :
        ALL_TRANSACTIONS += transactions
        print("size of all transaction: ",len(ALL_TRANSACTIONS))
    
    if not blockchain:
        block = Block()
    else:
        if blockchain[-1].can_add_transaction(ALL_TRANSACTIONS[LAST_TRANSACTION_INDEX]):
            block = blockchain = [-1]
        else:
            block = Block()

    while(block.can_add_transaction(ALL_TRANSACTIONS[LAST_TRANSACTION_INDEX]) and LAST_TRANSACTION_INDEX<len(ALL_TRANSACTIONS)):
        temp_transaction = ALL_TRANSACTIONS[LAST_TRANSACTION_INDEX]
        print("transaction #",LAST_TRANSACTION_INDEX)
        b1 = True
        try:
            verify_signature(temp_transaction)
            print("signature verified")
        except(ValueError,TypeError):
            b1 = False
            print("wrong signature")
        
        if b1 and check_balance(temp_transaction):
            block.verified_transaction.append(temp_transaction)
            execute_transaction(temp_transaction)
        else:
            print("non validated")
        
        print("pre incrementation")
        LAST_TRANSACTION_INDEX +=1
        print("post incrementation")
        if(LAST_TRANSACTION_INDEX<len(ALL_TRANSACTIONS)):
            if block.can_add_transaction(ALL_TRANSACTIONS[LAST_TRANSACTION_INDEX])==False:

                block.previous_block_hash = LAST_BLOCK_HASH
                block.Nonce = mine(block, 2)
                digest = hash(block)
                blockchain.append(block)
                LAST_BLOCK_HASH = digest

                block = Block()
                print("new block added")
            else:
                print("working on the same block")
        else:
            break

    blockchain.append(block)



if __name__ == "__main__":
    with app.app_context():
        #Med = Client(5000)
        #Med_info = ClientInfo("mohamed", b"123456", "image")
        #print("************")
        #create_database_client(Med, Med_info)
        #print("************")
        pass
    pass
    