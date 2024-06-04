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
CORS(app, resources={r"/Login/*": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/stocks/*": {"origins": "http://localhost:3000"}}, methods=["DELETE","GET"])
CORS(app, resources={r"/delete/*": {"origins": "http://localhost:3000"}}, methods=["DELETE"])
CORS(app, resources={r"/portfolio_management/*": {"origins": "http://localhost:3000"}}, methods=["GET"])
CORS(app, resources={r"/view_portfolio/*": {"origins": "http://localhost:3000"}}, methods=["GET","POST"])
CORS(app, resources={r"/upload_Docs/*": {"origins": "http://localhost:3000"}}, methods=["GET","POST"])


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


