from flask import Blueprint, jsonify, request
from firebase_admin import auth
from flask_cors import CORS,cross_origin
from firebase_admin import credentials, auth, initialize_app, firestore
import firebase_admin
from config.firebase_config import initialize_firebase_app

# Initialize Firebase
initialize_firebase_app()

# Initialize Firestore
db = firestore.client()
stocks_collection = db.collection("stocks")




getstocks_routes = Blueprint('getstocks_routes', __name__)
getstockid_routes = Blueprint('getstockid_routes', __name__)
poststocks_routes = Blueprint('poststocks_routes', __name__)
putstockid_routes = Blueprint('putstockid_routes', __name__)
delstockid_routes = Blueprint('delstockid_routes', __name__)

CORS(getstockid_routes)  # Enable CORS for your Flask app



# Create a new stock entry
@poststocks_routes.route('/stocks', methods=['POST'])
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
@getstocks_routes.route("/stocks", methods=["GET"])
@cross_origin()
def get_stocks():
    stocks = stocks_collection.stream()
    stock_list = [{"id": stock.id, **stock.to_dict()} for stock in stocks]
    return jsonify(stock_list), 200

# Get a specific stock by ID
@getstockid_routes.route("/specstockid", methods=["GET"])
@cross_origin()
def get_stock():
    stock_id = request.args.get('stock_id')
    if stock_id:
        stock = stocks_collection.document(stock_id).get()
        if stock.exists:
            return jsonify({"id": stock.id, **stock.to_dict()}), 200
        else:
            return jsonify({"error": "Stock not found"}), 404
    else:
        return jsonify({"error": "Missing stock_id parameter"}), 400



# Update a stock by ID
@putstockid_routes.route("/stockidupdate/<string:stock_id>", methods=["PUT"])
@cross_origin()
def update_stock(stock_id):
    data = request.get_json()
    stock_name = data["stock_name"]
    stock_ticker = data["stock_ticker"]

    stock_ref = stocks_collection.document(stock_id)
    stock_ref.update({"stock_name": stock_name, "stock_ticker": stock_ticker})
    return jsonify({"message": "Stock updated successfully"}), 200


# Delete a stock by ID

@delstockid_routes.route("/stockiddelete/<string:stock_id>", methods=["DELETE"])
@cross_origin()
def delete_stock(stock_id):
    stock_ref = stocks_collection.document(stock_id)
    stock_ref.delete()
    return jsonify({"message": "Stock deleted successfully"}), 200



# ######################################################################