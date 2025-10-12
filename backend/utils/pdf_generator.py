from fpdf import FPDF
import matplotlib.pyplot as plt
import json
import datetime

def create_pdf(profile, reports, output_path="report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CuraGenie Clinical Report", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)

    pdf.cell(0, 10, f"Name: {profile['first_name']} {profile['last_name']}", ln=True)
    pdf.cell(0, 10, f"Date of Birth: {profile['date_of_birth']}", ln=True)
    pdf.cell(0, 10, f"Gender: {profile['gender']}", ln=True)
    pdf.cell(0, 10, f"Email: {profile['email']}", ln=True)
    pdf.ln(10)

    for report in reports:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Report: {report['report_title']} ({report['report_type']})", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, f"Summary: {report['summary']}")
        pdf.multi_cell(0, 8, f"Recommendations: {report['recommendations']}")
        
        try:
            data = json.loads(report['report_data'])
            if isinstance(data, dict):
                plt.figure(figsize=(4,3))
                plt.bar(data.keys(), data.values(), color='skyblue')
                chart_path = f"temp_chart_{report['id']}.png"
                plt.savefig(chart_path)
                plt.close()
                pdf.image(chart_path, w=100)
        except:
            pass
        
        pdf.ln(10)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Generated on {datetime.date.today()}", ln=True, align='R')
    
    pdf.output(output_path)
    return output_path


# Run locally for testing
if __name__ == "__main__":
    profile = {
        "first_name": "Vishal",
        "last_name": "Chaudhary",
        "date_of_birth": "2003-04-15",
        "gender": "Male",
        "email": "vishal@example.com"
    }

    reports = [
        {
            "id": 1,
            "report_title": "Blood Analysis",
            "report_type": "Lab Test",
            "summary": "Blood test shows mild iron deficiency.",
            "recommendations": "Increase intake of leafy greens and supplements.",
            "report_data": json.dumps({"Hemoglobin": 13.5, "Iron": 60, "Vitamin D": 25})
        }
    ]

    create_pdf(profile, reports)
    print("✅ PDF generated successfully!")
