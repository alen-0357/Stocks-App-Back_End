
from flask import Blueprint, jsonify, request
from firebase_admin import auth
from flask_cors import CORS,cross_origin
from config.firebase_config import initialize_firebase_app
from firebase_admin import credentials, auth, initialize_app, firestore
from datetime import datetime, timedelta
import uuid

# Initialize Firebase
initialize_firebase_app()

# Initialize Firestore
db = firestore.client()
stocks_collection = db.collection("stocks")

posttransactions_routes = Blueprint('posttransactions_routes', __name__)
gettransactions_routes = Blueprint('gettransactions_routes', __name__)
gettransactionid_routes = Blueprint('gettransactionid_routes', __name__)


# Transaction operation


def is_stock_id_valid(stock_id):
    # Check if the stock_id exists in the 'stocks' collection
    stock_ref = db.collection('stocks').document(stock_id)
    return stock_ref.get().exists

def is_valid_transaction_type(transaction_type):
    return transaction_type.upper() in ['BUY', 'SELL']
####################################################################################
# Endpoint to add a new transaction
@posttransactions_routes.route('/transactions', methods=['POST'])
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

        # # If the transaction type is BUY, update the deposits collection
        # if data['transaction_type'].upper() == 'BUY':
        #     deposit_ref = db.collection('deposits').add({
        #         'userId': data.get('userId'),  # Ensure userId is included in the request data
        #         'Fund': -float(data['total_price']),
        #         'date': current_date
        #     })

        

        return jsonify({'success': True, 'transaction_id': transaction_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
###################################################################################################
@gettransactions_routes.route('/gettransactions', methods=['GET'])
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
                'Real id':transaction_data['transaction_id'],
                'stock_name': stock_name,
                'transaction_type': transaction_data['transaction_type'],
                'quantity': transaction_data['quantity'],
                'date': transaction_data['date'],
                'total_price': transaction_data['total_price']
            })

        return jsonify({"transactions": transactions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
 #######################################################################################   
# Endpoint to get all transactions for a single stock
@gettransactionid_routes.route('/gettransaction/<stock_id>', methods=['GET'])
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
    ###################################################################
