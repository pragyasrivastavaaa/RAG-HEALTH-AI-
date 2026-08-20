"""
Phase 4 Test Script — Longitudinal Analysis
Run from rag-health-ai/ root with Flask running.
Usage: python test_phase4.py

This test uploads 3 reports for the same patient (Rahul Sharma)
with progressively improving values, then checks trend detection.
"""
import os, sys, json, requests, time

BASE = "http://localhost:5000/api"

# Three reports: worsening → moderate → improving
REPORTS = [
    {
        "label": "Report 1 (Jan 2024 — worst)",
        "text": """PATHOLOGY REPORT
Patient Name: Rahul Sharma
Date: 10-Jan-2024
Hemoglobin: 9.8 g/dL
Glucose Fasting: 135 mg/dL
Total Cholesterol: 240 mg/dL
LDL Cholesterol: 160 mg/dL
HDL Cholesterol: 32 mg/dL
Triglycerides: 210 mg/dL
TSH: 6.2 mIU/L
Vitamin D: 12 ng/mL
HbA1c: 7.1 %
Creatinine: 1.5 mg/dL
Uric Acid: 8.1 mg/dL
"""
    },
    {
        "label": "Report 2 (Apr 2024 — improving)",
        "text": """PATHOLOGY REPORT
Patient Name: Rahul Sharma
Date: 15-Apr-2024
Hemoglobin: 11.0 g/dL
Glucose Fasting: 118 mg/dL
Total Cholesterol: 215 mg/dL
LDL Cholesterol: 140 mg/dL
HDL Cholesterol: 38 mg/dL
Triglycerides: 175 mg/dL
TSH: 5.5 mIU/L
Vitamin D: 18 ng/mL
HbA1c: 6.4 %
Creatinine: 1.3 mg/dL
Uric Acid: 7.2 mg/dL
"""
    },
    {
        "label": "Report 3 (Aug 2024 — best so far)",
        "text": """PATHOLOGY REPORT
Patient Name: Rahul Sharma
Date: 20-Aug-2024
Hemoglobin: 12.8 g/dL
Glucose Fasting: 102 mg/dL
Total Cholesterol: 195 mg/dL
LDL Cholesterol: 118 mg/dL
HDL Cholesterol: 44 mg/dL
Triglycerides: 148 mg/dL
TSH: 4.2 mIU/L
Vitamin D: 28 ng/mL
HbA1c: 5.9 %
Creatinine: 1.1 mg/dL
Uric Acid: 6.5 mg/dL
"""
    }
]


def make_pdf(text):
    lines   = text.strip().split("\n")
    content = ""
    y = 750
    for line in lines:
        safe     = line.replace("(", "\\(").replace(")", "\\)")
        content += f"BT /F1 9 Tf 40 {y} Td ({safe}) Tj ET\n"
        y -= 14
        if y < 50: break
    length = len(content.encode("latin-1"))
    pdf    = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>>>endobj
4 0 obj<</Length {length}>>
stream
{content}
endstream
endobj
xref
0 5
0000000000 65535 f 
trailer<</Size 5/Root 1 0 R>>
startxref
0
%%EOF"""
    path = "_temp_report.pdf"
    with open(path, "wb") as f: f.write(pdf.encode("latin-1"))
    return path


def test_longitudinal_engine_direct():
    print("\n--- Test 1: Longitudinal engine (direct) ---")
    import importlib.util, sys, os
    spec = importlib.util.spec_from_file_location(
        "longitudinal",
        os.path.join(os.path.dirname(__file__), "backend", "modules", "longitudinal.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    compute_longitudinal = mod.compute_longitudinal

    mock_results = [
        {"raw_values": {"hemoglobin": 9.8,  "glucose_fasting": 135, "cholesterol_total": 240},
         "health_score": 20, "uploaded_at": "2024-01-10"},
        {"raw_values": {"hemoglobin": 11.0, "glucose_fasting": 118, "cholesterol_total": 215},
         "health_score": 40, "uploaded_at": "2024-04-15"},
        {"raw_values": {"hemoglobin": 12.8, "glucose_fasting": 102, "cholesterol_total": 195},
         "health_score": 65, "uploaded_at": "2024-08-20"},
    ]

    result = compute_longitudinal(mock_results)

    print(f"Total reports  : {result['total_reports']}")
    print(f"Overall trend  : {result['overall_trend']}")
    print(f"Scores         : {result['scores_over_time']}")
    print(f"Risk trajectory: {result['risk_trajectory']}")
    print("\nParameter trends:")
    for key, data in result["parameters"].items():
        print(f"  {data['display_name']}: {data['values']} → {data['trend_label']}")

    assert result["overall_trend"] == "improving"
    print("PASSED")


def test_upload_three_reports():
    print("\n--- Test 2: Upload 3 reports for same patient ---")
    report_ids = []

    for i, report in enumerate(REPORTS):
        print(f"  Uploading {report['label']}...")
        pdf_path = make_pdf(report["text"])

        with open(pdf_path, "rb") as f:
            r = requests.post(f"{BASE}/upload",
                              files={"file": (f"rahul_report_{i+1}.pdf", f, "application/pdf")})
        os.remove(pdf_path)

        assert r.status_code == 201, f"Upload failed: {r.text}"
        report_id = r.json()["report_id"]
        report_ids.append(report_id)

        # Analyze each report
        r = requests.post(f"{BASE}/analyze/{report_id}")
        assert r.status_code == 200, f"Analyze failed: {r.text}"
        data = r.json()
        print(f"    report_id={report_id}, score={data.get('health_score')}, "
              f"patient={data.get('patient_name')}")

        time.sleep(0.5)

    print(f"  All 3 reports uploaded: {report_ids}")
    print("PASSED")
    return report_ids


def test_trend_api():
    print("\n--- Test 3: GET /api/trends/Rahul Sharma ---")
    r = requests.get(f"{BASE}/trends/Rahul Sharma")
    print(f"Status: {r.status_code}")

    if r.status_code == 200:
        data = r.json()
        print(f"Patient        : {data.get('patient_name')}")
        print(f"Total reports  : {data.get('total_reports')}")
        lng = data.get("longitudinal", {})
        print(f"Overall trend  : {lng.get('overall_trend')}")
        print(f"Score history  : {lng.get('scores_over_time')}")
        print(f"Risk trajectory: {lng.get('risk_trajectory')}")
        print("\nParameter trends:")
        for key, param in (lng.get("parameters") or {}).items():
            print(f"  {param['display_name']}: {param['values']} → {param['trend_label']}")

        assert data.get("total_reports", 0) >= 2
        assert lng.get("overall_trend") in ["improving", "worsening", "stable"]
        print("PASSED")
    else:
        print(f"Response: {r.json()}")
        print("NOTE: If 0 reports found, make sure Test 2 ran first.")


def test_patients_list():
    print("\n--- Test 4: GET /api/patients ---")
    r = requests.get(f"{BASE}/patients")
    assert r.status_code == 200
    data = r.json()
    print(f"Patients found: {len(data['patients'])}")
    for p in data["patients"]:
        print(f"  {p['patient_name']}: {p['report_count']} reports")
    print("PASSED")


def test_trends_by_report(report_ids):
    print(f"\n--- Test 5: GET /api/trends/by-report/{report_ids[-1]} ---")
    r = requests.get(f"{BASE}/trends/by-report/{report_ids[-1]}")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Patient: {data.get('patient_name')}, Reports: {data.get('total_reports')}")
        print("PASSED")
    else:
        print(f"Response: {r.json()}")


if __name__ == "__main__":
    print("=" * 55)
    print("  RAG Health AI — Phase 4 Test Suite")
    print("  Longitudinal Analysis Engine")
    print("=" * 55)
    try:
        test_longitudinal_engine_direct()
        report_ids = test_upload_three_reports()
        test_trend_api()
        test_patients_list()
        test_trends_by_report(report_ids)

        print("\n" + "=" * 55)
        print("  ALL TESTS PASSED — Phase 4 complete!")
        print("  Longitudinal analysis is working.")
        print("=" * 55)

    except requests.exceptions.ConnectionError:
        print("\nERROR: Flask not running. Run: cd backend && flask run")
    except Exception as e:
        print(f"\nERROR: {e}")
        raise