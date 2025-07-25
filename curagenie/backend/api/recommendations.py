

from flask import Blueprint, jsonify
from database import SessionLocal
from models.prs_score import PrsScore

from api.auth_middleware import verify_firebase_token
from api.rbac import requires_role

bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')

RISK_THRESHOLDS = {
    'alzheimers': 0.7,
    'diabetes': 0.7,
    'cancer': 0.7,
}
RECOMMENDATIONS = {
    'alzheimers': "High Alzheimer's Risk → Cognitive Tests",
    'diabetes': 'High Diabetes Risk → Blood Sugar Monitoring',
    'cancer': 'High Cancer Risk → Regular Screening',
}

@bp.route('/<user_id>', methods=['GET'])
@verify_firebase_token
@requires_role('user')
def get_recommendations(user_id):
    # Input validation
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    try:
        session = SessionLocal()
        scores = session.query(PrsScore).filter_by(user_id=user_id).all()
        recs = []
        for score_obj in scores:
            disease = score_obj.disease_type
            score = score_obj.score
            if disease in RISK_THRESHOLDS and score > RISK_THRESHOLDS[disease]:
                recs.append(RECOMMENDATIONS[disease])
        session.close()
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


    return jsonify({'user_id': user_id, 'recommendations': recs})
    # Audit log: Recommendations fetch
    try:
        from utils.audit import log_action
        log_action(user_id, 'RECOMMENDATIONS_FETCH', {'recommendations': recs})
    except Exception as e:
        pass
