from flask import Blueprint, request, jsonify
from database import SessionLocal

bp = Blueprint('ml_feedback', __name__, url_prefix='/api/ml')

@bp.route('/feedback', methods=['POST'])
def ml_feedback():
    data = request.get_json()
    prediction_id = data.get('prediction_id')
    is_correct = data.get('is_correct')
    comment = data.get('comment', '')
    # TODO: Store feedback in ml_predictions table
    # session = SessionLocal()
    # ... update ml_predictions with feedback ...
    # session.close()
    # For demo, just echo back
    return jsonify({
        'prediction_id': prediction_id,
        'is_correct': is_correct,
        'comment': comment,
        'status': 'feedback received'
    })
