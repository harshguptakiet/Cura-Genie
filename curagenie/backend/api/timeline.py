
from flask import Blueprint, jsonify
from database import SessionLocal
from models.genomic_data import GenomicData
from models.prs_score import PrsScore
from models.recommendation import Recommendation
import datetime
from api.auth_middleware import verify_firebase_token

bp = Blueprint('timeline', __name__, url_prefix='/api/timeline')

@bp.route('/<user_id>', methods=['GET'])
@verify_firebase_token
def get_timeline(user_id):
    # Input validation
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    try:
        session = SessionLocal()
        timeline = []
        uploads = session.query(GenomicData).filter_by(user_id=user_id).all()
        for upload in uploads:
            timeline.append({
                'date': upload.upload_date.strftime('%Y-%m-%d'),
                'type': 'Upload',
                'detail': f'{upload.file_type.upper()} file uploaded'
            })
        prs_scores = session.query(PrsScore).filter_by(user_id=user_id).all()
        for prs in prs_scores:
            timeline.append({
                'date': prs.calculation_date.strftime('%Y-%m-%d'),
                'type': 'PRS',
                'detail': f'{prs.disease_type.capitalize()} risk calculated'
            })
        recs = session.query(Recommendation).filter_by(user_id=user_id).all()
        for rec in recs:
            timeline.append({
                'date': rec.date_generated.strftime('%Y-%m-%d'),
                'type': 'Recommendation',
                'detail': rec.recommendation_text
            })
        session.close()
        timeline.sort(key=lambda x: x['date'])
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    # Log event (optional)
    # from utils.audit_log import log_event
    # log_event(user_id, 'get_timeline', None)

    return jsonify({'timeline': timeline})
