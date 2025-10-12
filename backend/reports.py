from fastapi import APIRouter, Response
from utils.pdf_generator import create_pdf
import json

router = APIRouter()

@router.get("/download-report/test")
def download_report_test():
    profile = {
        "first_name": "Test",
        "last_name": "User",
        "date_of_birth": "1999-01-01",
        "gender": "Female",
        "email": "test@example.com"
    }

    reports = [
        {
            "id": 1,
            "report_title": "Mock AI Health Report",
            "report_type": "Diagnostic",
            "summary": "AI detected mild irregularities in heart rate pattern.",
            "recommendations": "Consult a cardiologist and repeat test after 1 week.",
            "report_data": json.dumps({"Heart Rate": 82, "Oxygen Level": 97, "Stress Index": 35})
        }
    ]

    pdf_path = create_pdf(profile, reports)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return Response(content=pdf_bytes, media_type="application/pdf")
