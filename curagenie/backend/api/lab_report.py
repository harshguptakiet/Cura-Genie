from flask import Blueprint, request, jsonify

bp = Blueprint('lab_report', __name__, url_prefix='/api/lab-report')

@bp.route('/upload', methods=['POST'])
def upload_lab_report():
    # Placeholder for PDF lab report upload
    # TODO: Use PIL/OpenCV for OCR, spaCy for NLP
    # Example:
    # - Extract text from PDF
    # - Use spaCy to parse and extract key info
    return jsonify({'status': 'uploaded', 'info': 'PDF parsing placeholder'})
