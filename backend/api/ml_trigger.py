from flask import Blueprint, request, jsonify
import requests

bp = Blueprint('ml_trigger', __name__, url_prefix='/api/ml')

MODEL_ENDPOINTS = {
    'diabetes': 'http://localhost:6001/predict',
    'alzheimers': 'http://localhost:6002/predict',
    'tumor': 'http://localhost:6003/predict',
}

@bp.route('/trigger-prediction', methods=['POST'])
def trigger_prediction():
    data = request.get_json()
    disease_type = data.get('disease_type')
    input_data = data.get('input_data')
    if disease_type not in MODEL_ENDPOINTS:
        return jsonify({'error': 'Unknown disease type'}), 400
    try:
        res = requests.post(MODEL_ENDPOINTS[disease_type], json=input_data)
        prediction = res.json()
        return jsonify({'disease_type': disease_type, 'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
