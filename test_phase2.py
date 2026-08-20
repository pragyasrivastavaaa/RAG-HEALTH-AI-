"""
Phase 2 Test Script — NLP Parser + Knowledge Base Builder
Run from rag-health-ai/ root with Flask running.
Usage: python test_phase2.py
"""
import os, sys, json, requests

BASE = "http://localhost:5000/api"

SAMPLE_TEXT = """
PATHOLOGY REPORT
Patient Name: Rahul Sharma
Date: 15-Jan-2024

Hemoglobin          : 10.5 g/dL
RBC                 : 3.8 million/uL
WBC                 : 7500 cells/uL
Platelet Count      : 180000 cells/uL
Glucose Fasting     : 118 mg/dL
Glucose PP          : 165 mg/dL
HbA1c               : 6.2 %
Total Cholesterol   : 215 mg/dL
LDL Cholesterol     : 140 mg/dL
HDL Cholesterol     : 38 mg/dL
Triglycerides       : 175 mg/dL
TSH                 : 5.5 mIU/L
Vitamin D           : 18 ng/mL
Vitamin B12         : 180 pg/mL
SGPT (ALT)          : 52 U/L
SGOT (AST)          : 48 U/L
Creatinine          : 1.4 mg/dL
Uric Acid           : 7.2 mg/dL
"""


def test_nlp_parser():
    print("\n--- Test 1: NLP parser direct ---")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    from modules.nlp_parser import parse_lab_values
    from modules.name_extractor import extract_patient_name, extract_report_date

    values = parse_lab_values(SAMPLE_TEXT)
    name   = extract_patient_name(SAMPLE_TEXT)
    date   = extract_report_date(SAMPLE_TEXT)

    print(f"Parameters found : {len(values)}")
    print(f"Patient name     : {name}")
    print(f"Report date      : {date}")
    for k, v in values.items():
        print(f"  {k}: {v}")

    assert len(values) >= 10, "Should find at least 10 parameters"
    assert name is not None,  "Should extract patient name"
    print("PASSED")


def test_knowledge_base():
    print("\n--- Test 2: Knowledge base files exist ---")
    kb_dir = os.path.join(os.path.dirname(__file__), "knowledge_base")
    files  = [f for f in os.listdir(kb_dir) if f.endswith(".txt")]
    print(f"Knowledge files found: {files}")
    assert len(files) >= 2, "Need at least 2 knowledge base files"
    for f in files:
        path = os.path.join(kb_dir, f)
        size = os.path.getsize(path)
        print(f"  {f}: {size} bytes")
        assert size > 100, f"{f} is too small"
    print("PASSED")


def test_vector_store():
    print("\n--- Test 3: FAISS vector store exists ---")
    vs_dir   = os.path.join(os.path.dirname(__file__), "vector_store")
    faiss_f  = os.path.join(vs_dir, "index.faiss")
    pkl_f    = os.path.join(vs_dir, "index.pkl")

    if not os.path.exists(faiss_f):
        print("SKIP: Vector store not built yet.")
        print("Run: python backend/modules/knowledge_builder.py")
        return

    print(f"index.faiss: {os.path.getsize(faiss_f)} bytes")
    print(f"index.pkl  : {os.path.getsize(pkl_f)} bytes")
    print("PASSED")


def make_test_pdf():
    lines   = SAMPLE_TEXT.strip().split("\n")
    content = ""
    y       = 750
    for line in lines:
        safe    = line.replace("(", "\\(").replace(")", "\\)")
        content += f"BT /F1 9 Tf 40 {y} Td ({safe}) Tj ET\n"
        y -= 14
        if y < 50:
            break
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
    path = "_test_p2.pdf"
    with open(path, "wb") as f:
        f.write(pdf.encode("latin-1"))
    return path


def test_full_pipeline():
    print("\n--- Test 4: Full upload + analyze via Flask ---")
    pdf_path = make_test_pdf()

    with open(pdf_path, "rb") as f:
        r = requests.post(f"{BASE}/upload",
                          files={"file": ("blood_report.pdf", f, "application/pdf")})
    os.remove(pdf_path)
    assert r.status_code == 201
    report_id = r.json()["report_id"]
    print(f"Uploaded → report_id: {report_id}")

    r = requests.post(f"{BASE}/analyze/{report_id}")
    assert r.status_code == 200, f"Analyze failed: {r.text}"
    data = r.json()

    print(f"Patient name     : {data.get('patient_name')}")
    print(f"Report date      : {data.get('report_date')}")
    print(f"Parameters found : {data.get('parameters_found')}")
    print("Extracted values:")
    for item in data.get("extracted_values", []):
        print(f"  {item['display_name']}: {item['value']} {item['unit']}")

    assert data.get("parameters_found", 0) > 0
    print("PASSED")


if __name__ == "__main__":
    print("=" * 55)
    print("  RAG Health AI — Phase 2 Test Suite")
    print("  NLP Parser + Knowledge Base")
    print("=" * 55)
    try:
        test_nlp_parser()
        test_knowledge_base()
        test_vector_store()
        test_full_pipeline()
        print("\n" + "=" * 55)
        print("  Phase 2 tests complete!")
        print("=" * 55)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Flask not running. Run: cd backend && flask run")
    except Exception as e:
        print(f"\nERROR: {e}")
        raise