
from flask import Blueprint, request, jsonify
from database import SessionLocal

from api.auth_middleware import verify_firebase_token
from api.rbac import requires_role

bp = Blueprint('consent', __name__, url_prefix='/api/consent')

@bp.route('/agree', methods=['POST'])
@verify_firebase_token
@requires_role('user')
def agree_consent():
    data = request.get_json()
    user_id = data.get('user_id')
    feature_id = data.get('feature_id')
    version = data.get('version')
    user_agreement_timestamp = data.get('user_agreement_timestamp')
    ip_address = request.remote_addr
    # Input validation
    if not user_id or not feature_id or not version or not user_agreement_timestamp:
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        session = SessionLocal()
        # TODO: Insert into consent_records table
        # consent_record = ConsentRecord(...)
        # session.add(consent_record)
        # session.commit()
        session.close()
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    # Audit log: Consent agreement
    try:
        from utils.audit import log_action
        log_action(user_id, 'CONSENT_AGREE', {'feature_id': feature_id, 'version': version, 'timestamp': user_agreement_timestamp, 'ip': ip_address})
    except Exception as e:
        pass
    # log_event(user_id, 'agree_consent', feature_id)

    return jsonify({'status': 'consent recorded'})
