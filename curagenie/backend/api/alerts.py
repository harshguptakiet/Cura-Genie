from flask import Blueprint, jsonify
from database import SessionLocal
from models.user import User
# You may want to add a dedicated Alert model for production
from api.auth_middleware import verify_firebase_token

bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

@bp.route('/<user_id>', methods=['GET'])
@verify_firebase_token
def get_alerts(user_id):
    # Input validation
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    try:
        # For demo, return mock alerts
        alerts = [
            {'id': 1, 'message': 'High diabetes risk detected. Please consult your doctor.'},
            {'id': 2, 'message': 'New recommendation: Cognitive Tests advised.'}
        ]
    except Exception as e:
        return jsonify({'error': f'Alert error: {str(e)}'}), 500

    # Log event (optional)
    # from utils.audit_log import log_event
    # log_event(user_id, 'get_alerts', None)

    return jsonify({'alerts': alerts})
