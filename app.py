from datetime import datetime

import uuid
from flask import Flask, request, jsonify
from firebase_admin import credentials, auth, initialize_app, firestore

import firebase_admin
from flask_cors import CORS,cross_origin



app = Flask(__name__)
CORS(app, resources={r"/Login/*": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/stockslist/*": {"origins": "http://localhost:3000"}}, methods=["DELETE"])
CORS(app, resources={r"/delete/*": {"origins": "http://localhost:3000"}}, methods=["DELETE"])

# app.register_blueprint(stock_routes)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("/Pjs/back_end_firebase/stocks-9bc4d-firebase-adminsdk-58bc0-89141fb9ff.json")

firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()
stocks_collection = db.collection("stocks")


# Route for user registration
@app.route("/register", methods=["POST"])
@cross_origin()
def register():
    try:
        # Get user credentials from the request
        data = request.json
        email = data["email"]
        password = data["password"]

        # Create a new user with Firebase authentication
        user = auth.create_user(
            email=email,
            email_verified=False,
            password=password,
        )

        # Return success message
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
@cross_origin()
def login():
    try:
        # Get user credentials from the request
        data = request.json
        email = data["email"]
        password = data["password"]

        # Here you might want to validate the credentials on your server,
        # but authentication typically happens on the client side using
        # Firebase Authentication SDK.

        # You might send a token or some other identifier back to the client.

        return jsonify({"message": "Authentication successful"}), 200 
    
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    
@app.route("/users", methods=["GET"])
@cross_origin()
def list_users():
    try:
        # List all users from Firebase Authentication
        users = auth.list_users()

        # Extract relevant information for each user
        user_list = [
            {"uid": user.uid, "email": user.email} for user in users.users
        ]

        return jsonify({"users": user_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # ###############################################################
# Create a new stock entry
@app.route('/stocks', methods=['POST'])
@cross_origin()
def create_stock():
    try:
        data = request.get_json()
        stock_name = data['stock_name']
        stock_ticker = data['stock_ticker']

        new_stock_ref = stocks_collection.add({"stock_name": stock_name, "stock_ticker": stock_ticker})
        new_stock_id = new_stock_ref[1].id  # Assuming the ID is at index 1 in the tuple

        return jsonify({"Stock created Succesfully, id": new_stock_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get all stocks
@app.route("/stocks", methods=["GET"])
@cross_origin()
def get_stocks():
    stocks = stocks_collection.stream()
    stock_list = [{"id": stock.id, **stock.to_dict()} for stock in stocks]
    return jsonify(stock_list), 200


# Get a specific stock by ID
@app.route("/stockid/<string:stock_id>", methods=["GET"])
def get_stock(stock_id):
    stock = stocks_collection.document(stock_id).get()
    if stock.exists:
        return jsonify({"id": stock.id, **stock.to_dict()}), 200
    else:
        return jsonify({"error": "Stock not found"}), 404


# Update a stock by ID
@app.route("/stockidupdate/<string:stock_id>", methods=["PUT"])
@cross_origin()
def update_stock(stock_id):
    data = request.get_json()
    stock_name = data["stock_name"]
    stock_ticker = data["stock_ticker"]

    stock_ref = stocks_collection.document(stock_id)
    stock_ref.update({"stock_name": stock_name, "stock_ticker": stock_ticker})
    return jsonify({"message": "Stock updated successfully"}), 200


# Delete a stock by ID

@app.route("/stockiddelete/<string:stock_id>", methods=["DELETE"])
@cross_origin()
def delete_stock(stock_id):
    stock_ref = stocks_collection.document(stock_id)
    stock_ref.delete()
    return jsonify({"message": "Stock deleted successfully"}), 200



# ######################################################################
# #####################################################################
# Transaction operation


def is_stock_id_valid(stock_id):
    # Check if the stock_id exists in the 'stocks' collection
    stock_ref = db.collection('stocks').document(stock_id)
    return stock_ref.get().exists

def is_valid_transaction_type(transaction_type):
    return transaction_type.upper() in ['BUY', 'SELL']

# Endpoint to add a new transaction
@app.route('/transactions', methods=['POST'])
@cross_origin()
def add_transaction():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['stock_id', 'quantity', 'total_price','transaction_type']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if the provided stock_id is valid
        if not is_stock_id_valid(data['stock_id']):
            return jsonify({'error': f'Invalid stock_id: {data["stock_id"]}'}), 400
        
        
        if not is_valid_transaction_type(data['transaction_type']):
            return jsonify({"error": "Invalid transaction_type"}), 400

        # Generate a unique transaction ID using uuid
        transaction_id = str(uuid.uuid4())

        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Create a new transaction document in Firebase
        transaction_ref = db.collection('transactions').add({
            'stock_id': data['stock_id'],
            'transaction_id': transaction_id,
            'quantity': data['quantity'],
            'date': current_date,
            'total_price': data['total_price'],
            'transaction_type': data['transaction_type'].upper(),
        })

        return jsonify({'success': True, 'transaction_id': transaction_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/gettransactions', methods=['GET'])
@cross_origin()
def get_fulltransactions():
    try:
        # Fetch all transactions from Firestore
        db = firestore.client()  # Get Firestore client
        transactions_ref = db.collection('transactions')
        transactions_data = transactions_ref.stream()

        transactions = []
        for transaction in transactions_data:
            transaction_data = transaction.to_dict()
            stock_id = transaction_data['stock_id']

            # Fetch stock name using stock_id
            stocks_ref = db.collection('stocks')
            stock_data = stocks_ref.document(stock_id).get().to_dict()
            stock_name = stock_data['stock_name']

            transactions.append({
                'transaction_id': transaction.id,
                'stock_name': stock_name,
                'transaction_type': transaction_data['transaction_type'],
                'quantity': transaction_data['quantity'],
                'date': transaction_data['date'],
                'total_price': transaction_data['total_price']
            })

        return jsonify({"transactions": transactions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to get all transactions for a single stock
@app.route('/gettransaction/<stock_id>', methods=['GET'])
@cross_origin()
def get_transactions(stock_id):
    try:
        # Check if the provided stock_id is valid
        if not is_stock_id_valid(stock_id):
            return jsonify({'error': f'Invalid stock_id: {stock_id}'}), 400

        transactions = db.collection('transactions').where('stock_id', '==', stock_id).stream()
        transaction_list = [{'id': transaction.id, **transaction.to_dict()} for transaction in transactions]
        return jsonify({'transactions': transaction_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
# #####################################################################
if __name__ == "__main__":
    app.run(debug=True)
