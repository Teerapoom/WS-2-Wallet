
import json
from flask import Flask,jsonify,render_template,request
from web3 import Web3
from web3.auto import w3

app = Flask(__name__)
url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(url))

class contract_static:
    def __init__(self, private_key, sender_address, receiver_address, amount):
        self.private_key = private_key
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount

    def create_transaction(self):
        transaction = {
            'to': self.receiver_address,
            'value': web3.toWei(self.amount, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.toWei('50', 'gwei'),
            'nonce': web3.eth.getTransactionCount(self.sender_address)
        }
        return transaction


    def sign_transaction(self, transaction):
        signed_tx = web3.eth.account.signTransaction(transaction, self.private_key)
        return signed_tx


    def send_transaction(self, signed_tx):
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash

    def send(self):
        transaction = self.create_transaction()
        signed_tx = self.sign_transaction(transaction)
        tx_hash = self.send_transaction(signed_tx)
        return tx_hash

# Helper functions
def getBalance(address):
    return web3.fromWei(w3.eth.get_balance(address),"ether")


def getPrivateKey():
    my_file = open("Private.csv","r")
    keys = my_file.read().split("\n")
    my_file.close()
    return keys

def getAccountPair():
    keys = getPrivateKey()
    kp = []
    for i, (account, key) in enumerate(zip(w3.eth.accounts, keys)):
        object = {
            "address":account,
            "key":key
        }
        kp.append(object)
    return kp

def transfer(sender_addr,key,ether,recv_addr):
    transaction ={
        "to":recv_addr,
        "value":web3.toWei(ether,"ether"),
        "gas":21000,
        "gasPrice":w3.toWei("50","gwei"),
        "nonce":web3.eth.getTransactionCount(sender_addr)
    }
    signed_txn = w3.eth.account.sign_transaction(transaction,key)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return web3.toHex(tx_hash)

@app.route("/")
def index():
    accounts = getAccountPair()
    return render_template("home.html", accounts=accounts)


@app.route("/getbalance",methods=["POST"])
def tx_getbalance():
    data = request.json
    message = {
        "status":"success",
        "ether": getBalance(data['address'])
    }
    return jsonify(message),200

@app.route("/transfer",methods=["POST"])
def tx_transfe():
    data = request.json
    tx = data['tx']
    key = data['key']
    rx = data['rx']
    ether = data['ether']

    print(data)

    sender_address = w3.eth.account.privateKeyToAccount(key).address
    sender = contract_static(key, sender_address, rx, ether)
    tx_hash = sender.send()

    message = {
        "status": "Transfer success",
        "hash": tx_hash.hex(),
    }
    return jsonify(message), 200



if __name__ == "__main__":
    app.run(debug=True)