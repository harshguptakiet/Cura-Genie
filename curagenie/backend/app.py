from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api
import os
from api.genomic_data import bp as genomic_data_bp
from api.prs import bp as prs_bp
from api.recommendations import bp as recommendations_bp
from api.ehr import bp as ehr_bp
from api.external_dna import bp as external_dna_bp
from api.lab_report import bp as lab_report_bp
from api.wearables import bp as wearables_bp
from api.ml_trigger import bp as ml_trigger_bp
from api.ml_feedback import bp as ml_feedback_bp
from api.consent import bp as consent_bp
from api.timeline import bp as timeline_bp
from api.alerts import bp as alerts_bp
from api.prs_user import bp as prs_user_bp



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})
api = Api(app)
metrics = PrometheusMetrics(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[os.getenv("RATE_LIMIT", "100 per hour")]
)
app.register_blueprint(genomic_data_bp)
app.register_blueprint(prs_bp)
app.register_blueprint(recommendations_bp)
app.register_blueprint(ehr_bp)
app.register_blueprint(external_dna_bp)
app.register_blueprint(lab_report_bp)
app.register_blueprint(wearables_bp)
app.register_blueprint(ml_trigger_bp)
app.register_blueprint(ml_feedback_bp)
app.register_blueprint(consent_bp)
app.register_blueprint(timeline_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(prs_user_bp)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
