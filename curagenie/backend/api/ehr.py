from flask import Blueprint, jsonify

bp = Blueprint('ehr', __name__, url_prefix='/api/ehr')

@bp.route('/patient-data/<patient_id>', methods=['GET'])
def get_patient_data(patient_id):
    # Placeholder for FHIR-compliant patient data
    # Expected: { id, name, dob, gender, conditions, medications, ... }
    return jsonify({'patient_id': patient_id, 'data': 'FHIR patient data placeholder'})

@bp.route('/lab-results/<patient_id>', methods=['GET'])
def get_lab_results(patient_id):
    # Placeholder for FHIR-compliant lab results
    # Expected: { id, patient_id, results: [...] }
    return jsonify({'patient_id': patient_id, 'results': 'FHIR lab results placeholder'})
