from flask import Blueprint, request, jsonify

bp = Blueprint('wearables', __name__, url_prefix='/api/wearables')

@bp.route('/fitbit-data', methods=['POST'])
def fitbit_data():
    # Placeholder for Fitbit data ingestion
    return jsonify({'status': 'Fitbit data received'})

@bp.route('/apple-watch-data', methods=['POST'])
def apple_watch_data():
    # Placeholder for Apple Watch data ingestion
    return jsonify({'status': 'Apple Watch data received'})
