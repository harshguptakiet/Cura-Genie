# CuraGenie Backend

Flask-based API server for healthcare genomics platform.

## CuraGenie Backend

This is the Flask backend for CuraGenie. It provides RESTful APIs for genomic data processing, risk scoring, recommendations, and integrations with ML microservices and external services.

## Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```

## Endpoints
- `/health`: Health check endpoint

## Next Steps
- Add database connection (SQLAlchemy)
- Add S3 utilities
- Implement API endpoints for genomic data, PRS, recommendations, etc.
