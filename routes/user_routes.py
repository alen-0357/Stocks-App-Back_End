from flask import Blueprint, jsonify, request
from firebase_admin import auth
from flask_cors import CORS,cross_origin

user_routes = Blueprint('user_routes', __name__)

@user_routes.route("/users", methods=["GET"])
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
