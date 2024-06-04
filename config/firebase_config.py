# from firebase_admin import credentials, initialize_app

# def initialize_firebase_app():
#     cred = credentials.Certificate("/Pjs/back_end_firebase/stocks-9bc4d-firebase-adminsdk-58bc0-89141fb9ff.json")
#     firebase_app = initialize_app(cred)
#     return firebase_app
# #
from firebase_admin import credentials, initialize_app, get_app
from google.auth.transport import requests
from google.cloud import storage

def initialize_firebase_app():
    cred = credentials.Certificate("/Pjs/back_end_firebase/stocks-9bc4d-firebase-adminsdk-58bc0-89141fb9ff.json")
    
    try:
        # Try to get the existing app if it already exists
        firebase_app = get_app()
    except ValueError:
        # If the app doesn't exist, initialize it
        firebase_app = initialize_app(cred)

    return firebase_app