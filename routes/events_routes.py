from flask import Blueprint, jsonify, request
from firebase_admin import auth
from flask_cors import CORS,cross_origin
from firebase_admin import credentials, auth, initialize_app, firestore
import firebase_admin
from config.firebase_config import initialize_firebase_app
from datetime import datetime, timedelta
import logging

# Initialize Firebase
initialize_firebase_app()

# Initialize Firestore
db = firestore.client()
stocks_collection = db.collection("stocks")

addevents_routes = Blueprint('addevents_routes', __name__)
getevents_routes = Blueprint('getevents_routes', __name__)
getspecificevents_routes = Blueprint('getspecificevents_routes', __name__)


def is_stock_id_valid(stock_id):
    # Check if the stock_id exists in the 'stocks' collection
    stock_ref = db.collection('stocks').document(stock_id)
    return stock_ref.get().exists


    # Events 
    # Endpoint to add new events
@addevents_routes.route('/addevents', methods=['POST'])
@cross_origin()
def add_events():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['stock_id', 'event_description']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if the provided stock_id is valid
        if not is_stock_id_valid(data['stock_id']):
            return jsonify({'error': f'Invalid stock_id: {data["stock_id"]}'}), 400
        
        
      

        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Create a new transaction document in Firebase
        events_ref = db.collection('events').add({
            'stock_id': data['stock_id'],
            
            'event_description': data['event_description'],
            'date': current_date
          
        })

        return jsonify({'Event added successfully!': True}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
####################################################
@getevents_routes.route('/getevents', methods=['GET'])
@cross_origin()
def getevents():
    try:
        # Fetch all transactions from Firestore
        db = firestore.client()  # Get Firestore client
        events_ref = db.collection('events')
        events_data = events_ref.stream()

        events = []
        for event in events_data:
            events_data = event.to_dict()
            stock_id = events_data['stock_id']

            # Fetch stock name using stock_id
            stocks_ref = db.collection('stocks')
            stock_data = stocks_ref.document(stock_id).get().to_dict()
            stock_name = stock_data['stock_name']

            events.append({
                # 'event_id': event.id,
                'Event id' : events_data['event_id'],
                'stock_name': stock_name,
                'event_description': events_data['event_description'],
                'date': events_data['date'],
                'UserId':events_data['userId']
                
            })

        return jsonify({"events": events}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
###############################################################################
        # Endpoint to fetch events for a specific stock of a specific user
@getspecificevents_routes.route("/getspecificevents", methods=["GET"])
@cross_origin()
def stock_events_report():
    try:
        # Get parameters from the request (stock_id, start_date, end_date)
        stock_id = request.args.get("stock_id")
       

        # Get user ID from the headers
        userId = request.headers.get('Authorization')

        # Log the received user ID
        logging.info(f"Received user ID: {userId}")

        # Validate parameters if needed

        # Fetch transactions based on parameters and user ID
        events_ref = db.collection("events")

        if userId:
            events_ref = events_ref.where("userId", "==", userId)

        if stock_id:
            events_ref = events_ref.where("stock_id", "==", stock_id)

       

        events_data = events_ref.stream()

        # Convert transactions data to a list
        events = []
        for event in events_data:
            events_data = event.to_dict()
            events.append({
                
                "event_description": events_data["event_description"],
                
                "date": events_data["date"],
                
            })
            if not events:
             return jsonify({"No event descriptions available for the specified stock"}), 200

        return jsonify({"events": events}), 200
        
    except Exception as e:
        logging.error(f"Error in stock_transactions_report: {e}")
        return jsonify({"error": str(e)}), 500

    ########################################################################