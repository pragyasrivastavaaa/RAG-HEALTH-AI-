import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app import app
from config import Config
from database.db import init_db, insert_db
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def make_sample_pdf(path: str):
    c = canvas.Canvas(path, pagesize=letter)
    c.drawString(100, 700, "Blood Test Report")
    c.drawString(100, 680, "Hemoglobin: 12.3 g/dL")
    c.drawString(100, 660, "Glucose fasting: 102 mg/dL")
    c.drawString(100, 640, "Cholesterol total: 180 mg/dL")
    c.save()


def main():
    with app.app_context():
        init_db()
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        sample_path = os.path.join(Config.UPLOAD_FOLDER, "sample_report.pdf")
        make_sample_pdf(sample_path)

        report_id = insert_db(
            "INSERT INTO reports (filename, file_path) VALUES (?, ?)",
            ("sample_report.pdf", sample_path)
        )

        client = app.test_client()
        response = client.post(f"/api/analyze/{report_id}")
        print(f"status: {response.status_code}")
        print(response.get_data(as_text=True))

        if os.path.exists(sample_path):
            os.remove(sample_path)


if __name__ == "__main__":
    main()
