from flask import Blueprint, jsonify, request
from firebase_admin import auth
from flask_cors import CORS,cross_origin

register_routes = Blueprint('register_routes', __name__)


# Route for user registration
@register_routes.route("/register", methods=["POST"])
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
