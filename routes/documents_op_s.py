
from flask import Blueprint, jsonify, request
from firebase_admin import auth
from flask_cors import CORS,cross_origin
from config.firebase_config import initialize_firebase_app
from firebase_admin import credentials, auth, initialize_app, firestore
from datetime import datetime, timedelta
import uuid
import io
import requests
from PyPDF2 import PdfReader


# Initialize Firebase
initialize_firebase_app()

# Initialize Firestore
db = firestore.client()
stocks_collection = db.collection("stocks")

upload_routes = Blueprint('upload_routes', __name__)
delete_routes = Blueprint('delete_routes', __name__)
read_routes = Blueprint('read_routes', __name__)

# Endpoint to upload a document
@upload_routes.route('/upload_document', methods=['POST'])
@cross_origin()
def upload_document():
    try:
        data = request.get_json()

        # Validate if data is None or not in correct JSON format
        if data is None or not isinstance(data, dict):
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        # Validate required fields
        required_fields = [ 'file_name','file_url', 'date']
        # 'stock_id',-------/\
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Store document information in Firestore
        document_data = {
            'stock_id': data['stock_id'],
            'file_url': data['file_url'],
            'date': data['date'],
            'file_name':data['file_name']
        }
        document_ref = db.collection('uploaded_documents').add(document_data)

        # Extract document ID from the tuple
        document_id = document_ref[1].id if isinstance(document_ref, tuple) else document_ref.id

        return jsonify({'success': True, 'document_id': document_id}), 201
    except ValueError:
        return jsonify({'error': 'Invalid JSON data provided.'}), 400
    except Exception as e:
        error_message = str(e)
        print(f"Error uploading document: {error_message}")  # Log the error message
        return jsonify({'error': f'Failed to upload document to backend: {error_message}'}), 500
    
@delete_routes.route('/delete-upload', methods=['POST'])
@cross_origin()
def delete_upload():
    try:
        data = request.get_json()
        upload_id = data.get('upload_id')
         # Print the upload ID in the terminal
        print("Upload ID:", upload_id)

        if upload_id:
            # Delete the document from Firestore
            db.collection('uploaded_documents').document(upload_id).delete()
            return jsonify({'success': True, 'message': 'Upload deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Upload ID not provided'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@read_routes.route('/read-pdf', methods=['POST'])
@cross_origin()
def read_pdf():
    data = request.get_json()
    prev_uploads = data.get('prevUploads', [])
    pdf_summaries = []

    for upload in prev_uploads:
        file_url = upload.get('file_url')
        if file_url:
            print("PDF URL:", file_url)
            # Fetch the PDF file
            response = requests.get(file_url)
            if response.status_code == 200:
                # Read the first three words of the first page of the PDF
                pdf_data = response.content
                pdf_buffer = io.BytesIO(pdf_data)
                pdf_reader = PdfReader(pdf_buffer)
                first_page_text = pdf_reader.pages[0].extract_text()
                first_three_words = ' '.join(first_page_text.split()[:3])
                pdf_summaries.append(first_three_words)
            else:
                print(f"Failed to fetch PDF file from URL: {file_url}")
        else:
            print("No PDF URL found in the data.")

    return jsonify({'message': 'PDFs processed', 'pdfSummaries': pdf_summaries})

