from flask import Blueprint, jsonify, request
from firebase_admin import auth
from flask_cors import CORS,cross_origin

login_routes = Blueprint('login_routes', __name__)



@login_routes.route("/login", methods=["POST"])
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
    