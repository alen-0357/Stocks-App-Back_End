from datetime import datetime, timedelta
import uuid
from flask import Flask, request, jsonify
from firebase_admin import credentials, auth, initialize_app, firestore
import firebase_admin
from flask_cors import CORS,cross_origin
from google.cloud.exceptions import NotFound
import logging
from werkzeug.utils import secure_filename
import os   
from google.auth.transport import requests
from operator import itemgetter

from datetime import datetime, timedelta
import random


import io
import requests
from PyPDF2 import PdfReader
# from google.cloud import storage
# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
###############################################################
from config.firebase_config import initialize_firebase_app
from routes.user_routes import user_routes
from routes.documents_op_s import upload_routes,delete_routes,read_routes
from routes.register_routes import register_routes
from routes.login_routes import login_routes
from routes.stocks_routes import getstocks_routes, getstockid_routes, putstockid_routes, poststocks_routes, delstockid_routes
from routes.transactions_routes import gettransactions_routes,gettransactionid_routes,posttransactions_routes
from routes.events_routes import getevents_routes,getspecificevents_routes,addevents_routes
from routes.reports_routes import portfolio_routes,stockprofitreport_routes,stocktransactionsreport_routes, predict_stock_future_transactions_routes,fulltransactionsreport_routes,getprofitperdayreport_routes
###############################################################


app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app
CORS(app, resources={r"/Login/*": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/stocks/*": {"origins": "http://localhost:3000"}}, methods=["DELETE","GET"])
CORS(app, resources={r"/delete/*": {"origins": "http://localhost:3000"}}, methods=["DELETE"])
CORS(app, resources={r"/portfolio_management/*": {"origins": "http://localhost:3000"}}, methods=["GET"])
CORS(app, resources={r"/view_portfolio/*": {"origins": "http://localhost:3000"}}, methods=["GET","POST"])
CORS(app, resources={r"/upload_Docs/*": {"origins": "http://localhost:3000"}}, methods=["GET","POST"])
CORS(app, resources={r"/Home/*": {"origins": "http://localhost:3000"}}, methods=["DELETE"])
CORS(app, resources={r"/about_stocks/*": {"origins": "http://localhost:3000"}}, methods=["GET"])
# # # Initialize Firebase Admin SDK
# cred = credentials.Certificate("/Pjs/back_end_firebase/stocks-9bc4d-firebase-adminsdk-58bc0-89141fb9ff.json")


# firebase_admin.initialize_app(cred)
# Initialize Firebase
initialize_firebase_app()

# # Initialize Firestore
db = firestore.client()
# storage_client = storage.Client()
stocks_collection = db.collection("stocks")
######################################################
# User
app.register_blueprint(user_routes)  
app.register_blueprint(register_routes)  
app.register_blueprint(login_routes)  
# Documents Operations
app.register_blueprint(upload_routes)  
app.register_blueprint(delete_routes)  
app.register_blueprint(read_routes)  
# Stocks
app.register_blueprint(getstocks_routes)  
app.register_blueprint(getstockid_routes)  
app.register_blueprint(poststocks_routes)  
app.register_blueprint(putstockid_routes)  
app.register_blueprint(delstockid_routes)  
# Transactions
app.register_blueprint(gettransactions_routes)  
app.register_blueprint(gettransactionid_routes)  
app.register_blueprint(posttransactions_routes)  
# Events
app.register_blueprint(getevents_routes)  
app.register_blueprint(addevents_routes)  
app.register_blueprint(getspecificevents_routes)  

# Reports
app.register_blueprint(portfolio_routes)  
app.register_blueprint(stocktransactionsreport_routes)  
app.register_blueprint(stockprofitreport_routes)  
app.register_blueprint(predict_stock_future_transactions_routes)  
app.register_blueprint(fulltransactionsreport_routes)  
app.register_blueprint(getprofitperdayreport_routes)  

posts_collection = db.collection('posts')

@app.route('/upload_post', methods=['POST'])
@cross_origin()
def upload_post():
    try:
        data = request.get_json()
        user_id = request.headers.get('Authorization')

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        post_content = data.get('content')
        image_url = data.get('image_url', '')  # Get the image URL if provided

        if not post_content:
            return jsonify({"error": "Post content is required"}), 400

        # Create a new post document
        post = {
            'user_id': user_id,
            'content': post_content,
            'image_url': image_url,  # Include the image URL in the post
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        posts_collection.add(post)

        return jsonify({"success": True, "message": "Post uploaded successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/posts', methods=['GET'])
@cross_origin()
def get_posts():
    try:
        # Fetch posts from Firestore
        posts_ref = db.collection('posts')
        posts = []

        for doc in posts_ref.stream():
            post_data = doc.to_dict()
            post_data['id'] = doc.id  # Add document ID as 'id' field
            posts.append(post_data)

        return jsonify(posts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user/<string:user_id>')
@cross_origin()
def get_user_info(user_id):
    try:
        # Fetch user details from Firebase Authentication
        user = auth.get_user(user_id)
        
        # Extract relevant user information
        user_info = {
            'uid': user.uid,
            'email': user.email,
            
            # Add more fields as needed
        }
        print(f"Received request for {user_info} ")

        return jsonify(user_info), 200
    except auth.AuthError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

    

# Route to delete a post
@app.route('/delete_post/<string:post_id>', methods=['DELETE'])
@cross_origin()
def delete_post(post_id):
    try:
        # Get the user making the request
        user_token = request.headers.get('Authorization')
        user_id = user_token

        # Get the post from Firestore
        post_ref = db.collection('posts').document(post_id)
        post = post_ref.get()
        if not post.exists:
            return jsonify({'error': 'Post not found'}), 404

        post_data = post.to_dict()
        
        # Check if the user is the owner of the post
        if post_data['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Delete the post
        post_ref.delete()
        return jsonify({'success': True}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    # For realtime chart


    # Generate initial data for the past month
def generate_initial_data():
    data = []
    current_time = datetime.now()
    for i in range(15):
        day = current_time - timedelta(days=i)
        price = random.uniform(100, 200)  # Random price between 100 and 200
        data.append({"date": day.strftime("%Y-%m-%d %H:%M"), "price": price})
    return list(reversed(data))

# Store initial data
stock_data = generate_initial_data()

@app.route('/api/stock-data', methods=['GET'])
@cross_origin()
def get_stock_data():
    return jsonify(stock_data)

@app.route('/api/update-price', methods=['GET'])
@cross_origin()
def update_price():
    global stock_data
    # Simulate price update
    last_price = stock_data[-1]['price']
    new_price = last_price + random.uniform(-5, 5)  # Random fluctuation
    stock_data.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "price": new_price
    })
    # Keep only the last 10 days of data
    stock_data = stock_data[-10:]
    return jsonify(stock_data)

    ###################################


# # Route to like a post
# @app.route('/like_post/<post_id>', methods=['POST'])
# @cross_origin()
# def like_post(post_id):
#     try:
#         # Simulate getting user ID from Authorization header
#         user_id = request.headers.get('Authorization')

#         # Fetch post document
#         post_ref = db.collection('posts').document(post_id)
#         post = post_ref.get()

#         if not post.exists:
#             return jsonify({'error': 'Post not found'}), 404

#         # Check if user has already liked the post
#         if user_id in post.to_dict().get('likes', []):
#             return jsonify({'success': False, 'message': 'Already liked this post'}), 200

#         # Add user ID to likes array
#         post_ref.update({
#             'likes': firestore.ArrayUnion([user_id])
#         })

#         # Fetch updated post data
#         updated_post = post_ref.get().to_dict()

#         return jsonify({'success': True, 'likes': updated_post.get('likes', [])}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
