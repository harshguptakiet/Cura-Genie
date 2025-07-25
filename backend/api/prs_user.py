from flask import Blueprint, jsonify
from database import SessionLocal
from models.prs_score import PrsScore

bp = Blueprint('prs_user', __name__, url_prefix='/api/prs/user')

@bp.route('/<user_id>', methods=['GET'])
def get_prs_scores(user_id):
    session = SessionLocal()
    scores = session.query(PrsScore).filter_by(user_id=user_id).all()
    result = [
        {
            'disease_type': s.disease_type,
            'score': s.score
        } for s in scores
    ]
    session.close()
    return jsonify({'scores': result})
