import logging
from flask import Blueprint, jsonify, request
from firebase_admin import auth
from flask_cors import CORS,cross_origin
from firebase_admin import credentials, auth, initialize_app, firestore
import firebase_admin
from config.firebase_config import initialize_firebase_app
import requests
import random
from datetime import datetime, timedelta
from operator import itemgetter

# Initialize Firebase
initialize_firebase_app()

# Initialize Firestore
db = firestore.client()
stocks_collection = db.collection("stocks")

stocktransactionsreport_routes = Blueprint('stocktransactionsreport_routes', __name__)
stockprofitreport_routes = Blueprint('stockprofitreport_routes', __name__)
portfolio_routes = Blueprint('portfolio_routes', __name__)
predict_stock_future_transactions_routes = Blueprint('predict_stock_future_transactions_routes', __name__)
fulltransactionsreport_routes = Blueprint('fulltransactionsreport_routes', __name__)
getprofitperdayreport_routes = Blueprint('getprofitperdayreport_routes', __name__)



    # Endpoint to fetch transactions for a specific stock within a date range
@stocktransactionsreport_routes.route("/stocktransactionsreport", methods=["GET"])
@cross_origin()
def stock_transactions_report():
    try:
        # Get parameters from the request (stock_id, start_date, end_date)
        stock_id = request.args.get("stock_id")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        # Get user ID from the headers
        userId = request.headers.get('Authorization')

        # Log the received user ID
        logging.info(f"Received user ID: {userId}")

        # Validate parameters if needed

        # Fetch transactions based on parameters and user ID
        transactions_ref = db.collection("transactions")

        if userId:
            transactions_ref = transactions_ref.where("userId", "==", userId)

        if stock_id:
            transactions_ref = transactions_ref.where("stock_id", "==", stock_id)

        if start_date and end_date:
            transactions_ref = transactions_ref.where("date", ">=", start_date).where("date", "<=", end_date)

        transactions_data = transactions_ref.stream()

        # Convert transactions data to a list
        transactions = []
        for transaction in transactions_data:
            transaction_data = transaction.to_dict()
            transactions.append({
                "transaction_id": transaction.id,
                'transaction_type': transaction_data["transaction_type"],
                "quantity": transaction_data["quantity"],
                "date": transaction_data["date"],
                "total_price": transaction_data["total_price"]
            })

        return jsonify({"transactions": transactions}), 200

    except Exception as e:
        logging.error(f"Error in stock_transactions_report: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint to get profit for a specific stock within a date range
@stockprofitreport_routes.route("/stockprofitreport", methods=["GET"])
@cross_origin()
def stock_profit_report():
    try:
        # Get parameters from the request (stock_id, start_date, end_date)
        stock_id = request.args.get("stock_id")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        # Get user ID from the headers
        userId = request.headers.get('Authorization')

        # Log the received user ID
        logging.info(f"Received user ID: {userId}")

        # Validate parameters if needed

        # Fetch transactions based on parameters and user ID
        transactions_ref = db.collection("transactions")

        if userId:
            transactions_ref = transactions_ref.where("userId", "==", userId)

        if stock_id:
            transactions_ref = transactions_ref.where("stock_id", "==", stock_id)

        if start_date and end_date:
            transactions_ref = transactions_ref.where("date", ">=", start_date).where("date", "<=", end_date)

        transactions_data = transactions_ref.stream()

        # Calculate profit
        total_buy_price = 0
        total_sell_price = 0

        for transaction in transactions_data:
            transaction_data = transaction.to_dict()
            quantity = float(transaction_data["quantity"])
            total_price = float(transaction_data["total_price"])
            if transaction_data["transaction_type"] == "BUY":
                total_buy_price += quantity * total_price
            elif transaction_data["transaction_type"] == "SELL":
                total_sell_price += quantity * total_price

     # Ensure that total_sell_price is greater than or equal to total_buy_price
        if total_sell_price >= total_buy_price:
            profit = total_sell_price - total_buy_price
            loss = 0
        else:
            profit = 0
            loss = total_buy_price - total_sell_price

        return jsonify({"profit": profit, "loss": loss}), 200

    except Exception as e:
        logging.error(f"Error in stock_profit_report: {e}")
        return jsonify({"error": str(e)}), 500
##########################################################################
##############################################################################
# @portfolio_routes.route('/portfolio/<transaction_type>', methods=['GET'])
# @cross_origin()
# def get_portfolio(transaction_type):
#     try:
#         # Get the user ID from the request headers
#         user_token = request.headers.get('Authorization')
#         userId = user_token

#         # Log the received user ID
#         # logging.info(f"Received user ID: {userId}")
#         logging.info(f"Received user ID: {userId}, Transaction Type: {transaction_type}")

#         # Dictionary to store stock data
#         portfolio_data = {}

#         # Query transactions with transaction_type 'BUY' for the specific user
#         transactions = db.collection('transactions').where('transaction_type', '==',  transaction_type).where('userId', '==', userId).stream()


#         # Iterate through transactions
#         for transaction in transactions:
#             transaction_data = transaction.to_dict()

#             stock_id = transaction_data['stock_id']
#             quantity = transaction_data['quantity']
#             total_price = transaction_data['total_price']

#             # If stock_id is not in portfolio_data, initialize it
#             if stock_id not in portfolio_data:
#                 portfolio_data[stock_id] = {
#                     'stock_name': get_stock_name(stock_id),
#                     'total_quantity': 0,
#                     'total_price': 0
#                 }

#             # Update total_quantity and total_price
#             portfolio_data[stock_id]['total_quantity'] += quantity
#             portfolio_data[stock_id]['total_price'] += total_price

#         # Convert the data to a list for JSON response
#         portfolio_list = list(portfolio_data.values())

#         return jsonify(portfolio_list), 200

#     except firebase_admin.auth.InvalidIdTokenError as e:
#         return jsonify({"error": "Invalid ID token"}), 401
#     except firebase_admin.auth.ExpiredIdTokenError as e:
#         return jsonify({"error": "Expired ID token"}), 401
#     except Exception as e:
#         logging.error(f"Error in get_portfolio: {e}")
#         return jsonify({"error": "Internal server error"}), 500

# def get_stock_name(stock_id):
#     # Function to get stock_name from stocks collection based on stock_id
#     stock_doc = db.collection('stocks').document(stock_id).get()
#     if stock_doc.exists:
#         return stock_doc.to_dict()['stock_name']
#     return None
##############################################################################
@portfolio_routes.route('/portfolio/<transaction_type>', methods=['GET'])
@cross_origin()
def get_portfolio(transaction_type):
    try:
        # Get the user ID from the request headers
        user_token = request.headers.get('Authorization')
        userId = user_token

        # Log the received user ID
        # logging.info(f"Received user ID: {userId}")
        logging.info(f"Received user ID: {userId}, Transaction Type: {transaction_type}")

        # Dictionary to store stock data
        portfolio_data = {}

        # Query transactions with the specified transaction type for the specific user
        transactions = db.collection('transactions').where('transaction_type', '==',  transaction_type).where('userId', '==', userId).stream()

        # Iterate through transactions
        for transaction in transactions:
            transaction_data = transaction.to_dict()

            stock_id = transaction_data['stock_id']
            quantity = transaction_data['quantity']
            total_price_per_unit = transaction_data['total_price']  # Using total_price as unit price

            # If stock_id is not in portfolio_data, initialize it
            if stock_id not in portfolio_data:
                portfolio_data[stock_id] = {
                    'stock_name': get_stock_name(stock_id),
                    'total_quantity': 0,
                    'total_price': 0
                }

            # Update total_quantity and total_price
            portfolio_data[stock_id]['total_quantity'] += quantity
            portfolio_data[stock_id]['total_price'] += quantity * total_price_per_unit

        # Convert the data to a list for JSON response
        portfolio_list = list(portfolio_data.values())

        return jsonify(portfolio_list), 200

    except firebase_admin.auth.InvalidIdTokenError as e:
        return jsonify({"error": "Invalid ID token"}), 401
    except firebase_admin.auth.ExpiredIdTokenError as e:
        return jsonify({"error": "Expired ID token"}), 401
    except Exception as e:
        logging.error(f"Error in get_portfolio: {e}")
        return jsonify({"error": "Internal server error"}), 500

def get_stock_name(stock_id):
    # Function to get stock_name from stocks collection based on stock_id
    stock_doc = db.collection('stocks').document(stock_id).get()
    if stock_doc.exists:
        return stock_doc.to_dict()['stock_name']
    return None
##############################################################################




@predict_stock_future_transactions_routes.route('/predict_stock_future_transactions', methods=['POST'])
@cross_origin()
def predict_stock_future_transactions():
    try:
        # Get stock_id and end_date from the frontend
        stock_id = request.json.get('stock_id')
        end_date = request.json.get('end_date')

        # Print stock_id and end_date in the terminal
        print(f"Received request for stock_id: {stock_id}, end_date: {end_date}")

        # Fetch stock details for the given stock_id
        stock_details_response = requests.get(f'http://127.0.0.1:5000/gettransaction/{stock_id}')
        stock_details_response.raise_for_status()
        stock_data = stock_details_response.json()

        # Extract transactions from the response
        transactions = stock_data.get('transactions', [])

        # Check if transactions are available
        if not transactions:
            raise ValueError(f"No transactions available for stock_id: {stock_id}")

        # Generate random future predictions for the next 5 days
        future_dates = [datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=i) for i in range(1, 6)]
        future_predictions = ['BUY' if random.random() < 0.5 else 'SELL' for _ in range(5)]

        result = {
            'stock_id': stock_id,
            'end_date': end_date,
            'future_predictions': list(zip([date.strftime('%Y-%m-%d') for date in future_dates], future_predictions))
        }

        return jsonify(result), 200

    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock details: {str(e)}")
        return jsonify({'error': f"Error fetching stock details: {str(e)}"}), 500
    except ValueError as ve:
        print(f"ValueError: {str(ve)}")
        return jsonify({'error': str(ve)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@fulltransactionsreport_routes.route("/fullstockstransactionsreport", methods=["GET"])
@cross_origin()
def stock_transactions_report():
    try:
        # Get parameters from the request
        stock_id = request.args.get("stock_id")
        user_id = request.headers.get('Authorization')

        # Validate parameters
        if not stock_id or not user_id:
            error_message = "Both 'stock_id' and 'user_id' must be provided."
            logging.error(error_message)
            return jsonify({"error": error_message}), 400

        # Log the received user ID
        logging.info(f"Received user ID: {user_id}")

        # Fetch transactions based on parameters and user ID
        transactions_ref = db.collection("transactions")

        if user_id:
            transactions_ref = transactions_ref.where("userId", "==", user_id)

        if stock_id:
            transactions_ref = transactions_ref.where("stock_id", "==", stock_id)

        transactions_data = transactions_ref.stream()

        # Convert transactions data to a list
        transactions = []
        for transaction in transactions_data:
            transaction_data = transaction.to_dict()
            transactions.append({
                "transaction_id": transaction.id,
                'transaction_type': transaction_data["transaction_type"],
                "quantity": transaction_data["quantity"],
                "date": transaction_data["date"],
                "total_price": transaction_data["total_price"]
            })

        return jsonify({"transactions": transactions}), 200

    except Exception as e:
        logging.error(f"Error in stock_transactions_report: {e}")
        return jsonify({"error": str(e)}), 500
    

@getprofitperdayreport_routes.route("/getprofitperdayreport", methods=["GET"])
@cross_origin()
def perday_profit_report():
    try:
        # Get parameters from the request
        stock_id = request.args.get("stock_id")
        user_id = request.headers.get('Authorization')

        # Validate parameters
        if not stock_id or not user_id:
            error_message = "Both 'stock_id' and 'user_id' must be provided."
            logging.error(error_message)
            return jsonify({"error": error_message}), 400

        # Log the received user ID
        logging.info(f"Received user ID: {user_id}")

        # Fetch transactions based on parameters and user ID
        transactions_ref = db.collection("transactions")

        if user_id:
            transactions_ref = transactions_ref.where("userId", "==", user_id)

        if stock_id:
            transactions_ref = transactions_ref.where("stock_id", "==", stock_id)

        transactions_data = transactions_ref.stream()

        # Initialize a list to store daily transaction data
        daily_transactions = []

        # Iterate through transactions and aggregate data for each day
        for transaction in transactions_data:
            transaction_data = transaction.to_dict()
            date = datetime.strptime(transaction_data['date'], '%Y-%m-%d').date()

            # Convert date to string for use as dictionary key
            date_str = date.strftime('%Y-%m-%d')

            # Sort the daily_transactions list by date
            daily_transactions.sort(key=itemgetter('date'))

            # Initialize daily transaction data if not exists
            if not any(d['date'] == date_str for d in daily_transactions):
                daily_transactions.append({
                    'date': date_str,
                    'total_cost_buy': 0,
                    'total_cost_sell': 0,
                    'total_revenue_sell': 0
                })

            if transaction_data['transaction_type'] == 'BUY':
                for item in daily_transactions:
                    if item['date'] == date_str:
                        item['total_cost_buy'] += transaction_data['quantity'] * transaction_data['total_price']
            elif transaction_data['transaction_type'] == 'SELL':
                for item in daily_transactions:
                    if item['date'] == date_str:
                        item['total_cost_sell'] += transaction_data['quantity'] * transaction_data['total_price']
                        item['total_revenue_sell'] += transaction_data['quantity'] * transaction_data['total_price']

        # Calculate profit or loss percentage for each day
        for data in daily_transactions:
            total_cost_buy = data['total_cost_buy']
            total_cost_sell = data['total_cost_sell']
            total_revenue_sell = data['total_revenue_sell']

            if total_cost_buy == 0:
                # Handle division by zero error
                profit_loss_percentage = 0
            else:
                profit_loss_percentage = ((total_revenue_sell - total_cost_buy) / total_cost_buy) * 100

                 # Round profit/loss percentage to two decimal points
            profit_loss_percentage = round(profit_loss_percentage, 2)

            # Update daily transaction data with profit/loss percentage
            data['profit_loss_percentage'] = profit_loss_percentage

            

        # Return the aggregated daily transactions as JSON
        return jsonify({"profit": daily_transactions})
        
        

    except Exception as e:
        logging.error(f"Error in stock_transactions_report: {e}")
        return jsonify({"error": str(e)}), 500
    