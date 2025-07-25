

from flask import Blueprint, request, jsonify
import random
from database import SessionLocal
from models.prs_score import PrsScore
import uuid

from api.auth_middleware import verify_firebase_token
from api.rbac import requires_role

bp = Blueprint('prs', __name__, url_prefix='/api/prs')

@bp.route('/calculate', methods=['POST'])
@verify_firebase_token
@requires_role('doctor')
def calculate_prs():
    data = request.get_json()
    genomic_data_id = data.get('genomic_data_id')
    disease_type = data.get('disease_type')
    user_id = data.get('user_id')
    # Input validation
    if not genomic_data_id or not disease_type or not user_id:
        return jsonify({'error': 'Missing required fields'}), 400
    if disease_type not in ['diabetes', 'alzheimers', 'cancer']:
        return jsonify({'error': 'Invalid disease type'}), 400

    try:
        # TODO: Replace with real XGBoost model inference
        score = round(random.uniform(0, 1), 3)
    except Exception as e:
        return jsonify({'error': f'PRS calculation error: {str(e)}'}), 500

    # Store PRS score in PostgreSQL
    # Audit log: PRS calculation
    try:
        from utils.audit import log_action
        log_action(user_id, 'PRS_CALCULATION', {'genomic_data_id': genomic_data_id, 'disease_type': disease_type})
    except Exception as e:
        pass  # Logging failure should not block main flow
    try:
        session = SessionLocal()
        new_id = str(uuid.uuid4())
        prs_score = PrsScore(
            id=new_id,
            user_id=user_id,
            genomic_data_id=genomic_data_id,
            disease_type=disease_type,
            score=score
        )
        session.add(prs_score)
        session.commit()
        session.close()
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    # Log event (optional)
    # from utils.audit_log import log_event
    # log_event(user_id, 'calculate_prs', new_id)

    return jsonify({
        'id': new_id,
        'genomic_data_id': genomic_data_id,
        'disease_type': disease_type,
        'score': score,
        'status': 'calculated'
    })
