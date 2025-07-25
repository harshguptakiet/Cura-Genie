from functools import wraps
from flask import request, jsonify
import os
import firebase_admin
from firebase_admin import auth, credentials

# Initialize Firebase Admin SDK (example, use your credentials file)
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase_creds.json'))
    firebase_admin.initialize_app(cred)

def verify_firebase_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split('Bearer ')[-1]
        if not token:
            return jsonify({'error': 'Missing auth token'}), 401
        try:
            decoded = auth.verify_id_token(token)
            request.user = decoded
        except Exception:
            return jsonify({'error': 'Invalid or expired token'}), 401
        return f(*args, **kwargs)
    return decorated
