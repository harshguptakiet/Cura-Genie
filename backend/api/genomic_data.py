
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
from s3_utils import upload_file_to_s3
from database import SessionLocal
from Bio import SeqIO
import vcfpy
import uuid
from models.genomic_data import GenomicData

bp = Blueprint('genomic_data', __name__, url_prefix='/api/genomic-data')

@bp.route('/upload', methods=['POST'])
def upload_genomic_data():
    # Input validation
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    user_id = request.form.get('user_id', None)
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    filename = secure_filename(file.filename)
    if not (filename.endswith('.vcf') or filename.endswith('.fastq')):
        return jsonify({'error': 'Invalid file type. Only VCF/FASTQ allowed.'}), 400

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, filename)
    try:
        file.save(temp_path)
    except Exception as e:
        return jsonify({'error': f'File save error: {str(e)}'}), 500

    # Upload to S3
    s3_key = f"genomic_data/{filename}"
    try:
        with open(temp_path, 'rb') as f:
            success = upload_file_to_s3(f, os.getenv('AWS_S3_BUCKET'), s3_key)
        if not success:
            os.remove(temp_path)
            os.rmdir(temp_dir)
            return jsonify({'error': 'S3 upload failed'}), 500
    except Exception as e:
        os.remove(temp_path)
        os.rmdir(temp_dir)
        return jsonify({'error': f'S3 upload error: {str(e)}'}), 500

    # Parse file and extract metadata
    metadata = {}
    try:
        if filename.endswith('.vcf'):
            vcf_reader = vcfpy.Reader.from_path(temp_path)
            metadata['variants_count'] = sum(1 for _ in vcf_reader)
        elif filename.endswith('.fastq'):
            records = list(SeqIO.parse(temp_path, 'fastq'))
            metadata['reads_count'] = len(records)
    except Exception as e:
        metadata['error'] = str(e)

    # Store metadata in PostgreSQL
    try:
        session = SessionLocal()
        new_id = str(uuid.uuid4())
        genomic_data = GenomicData(
            id=new_id,
            user_id=user_id,
            file_name=filename,
            s3_key=s3_key,
            file_type='vcf' if filename.endswith('.vcf') else 'fastq',
            status='uploaded',
            metadata_json=metadata
        )
        session.add(genomic_data)
        session.commit()
        session.close()
    except Exception as e:
        os.remove(temp_path)
        os.rmdir(temp_dir)
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    # Clean up temp file
    try:
        os.remove(temp_path)
        os.rmdir(temp_dir)
    except Exception:
        pass

    # Log event (optional)
    # from utils.audit_log import log_event
    # log_event(user_id, 'upload_genomic_data', new_id)

    return jsonify({'id': new_id, 's3_key': s3_key, 'status': 'uploaded', 'metadata': metadata})
