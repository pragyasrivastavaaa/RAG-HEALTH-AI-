"""
Phase 1 Test Script — Multimodal Extraction + Upload API
Run from rag-health-ai/ root with Flask running.
Usage: python test_phase1.py
"""
import os, sys, requests

BASE = "http://localhost:5000/api"

# ── Test 1: OCR extractor unit test ───────────────────────────────────────
def test_ocr_direct():
    print("\n--- Test 1: OCR extractor (direct, no Flask) ---")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    from modules.ocr_extractor import extract_text, _digital_pdf_extract

    # Create a minimal test PDF
    pdf_path = "_test_ocr.pdf"
    lines    = ["PATHOLOGY REPORT", "Hemoglobin: 11.2 g/dL", "Glucose Fasting: 118 mg/dL"]
    content  = "\n".join(f"BT /F1 10 Tf 50 {750-i*20} Td ({l}) Tj ET" for i,l in enumerate(lines))
    length   = len(content.encode("latin-1"))
    pdf_bytes = f"""%PDF-1.4
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
%%EOF""".encode("latin-1")
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

    text = extract_text(pdf_path)
    os.remove(pdf_path)
    print(f"Extracted {len(text)} characters")
    print(f"Preview: {text[:150].strip()}")
    assert len(text) > 10, "Extraction returned too little text"
    print("PASSED")


# ── Test 2: Home route ─────────────────────────────────────────────────────
def test_home():
    print("\n--- Test 2: Flask home route ---")
    r = requests.get("http://localhost:5000/")
    print(f"Status: {r.status_code}  →  {r.json()}")
    assert r.status_code == 200
    print("PASSED")


# ── Test 3: Upload PDF ─────────────────────────────────────────────────────
def test_upload_pdf():
    print("\n--- Test 3: Upload PDF ---")
    pdf_path = "_upload_test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog>>\nendobj\n%%EOF")
    with open(pdf_path, "rb") as f:
        r = requests.post(f"{BASE}/upload", files={"file": ("blood_test.pdf", f, "application/pdf")})
    os.remove(pdf_path)
    print(f"Status: {r.status_code}  →  {r.json()}")
    assert r.status_code == 201
    assert "report_id" in r.json()
    print("PASSED")
    return r.json()["report_id"]


# ── Test 4: Wrong file type ────────────────────────────────────────────────
def test_upload_invalid():
    print("\n--- Test 4: Upload invalid file type ---")
    r = requests.post(f"{BASE}/upload", files={"file": ("virus.exe", b"MZ", "application/octet-stream")})
    print(f"Status: {r.status_code}  →  {r.json()}")
    assert r.status_code == 400
    print("PASSED")


# ── Test 5: Get all reports ────────────────────────────────────────────────
def test_get_reports():
    print("\n--- Test 5: Get all reports ---")
    r = requests.get(f"{BASE}/reports")
    print(f"Status: {r.status_code}, Total: {len(r.json()['reports'])}")
    assert r.status_code == 200
    print("PASSED")


# ── Test 6: Get single report ──────────────────────────────────────────────
def test_get_report(report_id):
    print(f"\n--- Test 6: Get report #{report_id} ---")
    r = requests.get(f"{BASE}/report/{report_id}")
    print(f"Status: {r.status_code}  →  {r.json()}")
    assert r.status_code == 200
    print("PASSED")


# ── Test 7: 404 for missing report ────────────────────────────────────────
def test_report_not_found():
    print("\n--- Test 7: Report not found (404) ---")
    r = requests.get(f"{BASE}/report/9999")
    print(f"Status: {r.status_code}")
    assert r.status_code == 404
    print("PASSED")


if __name__ == "__main__":
    print("=" * 55)
    print("  RAG Health AI — Phase 1 Test Suite")
    print("  Multimodal Extraction + Upload API")
    print("=" * 55)
    try:
        test_ocr_direct()
        test_home()
        report_id = test_upload_pdf()
        test_upload_invalid()
        test_get_reports()
        test_get_report(report_id)
        test_report_not_found()
        print("\n" + "=" * 55)
        print("  ALL TESTS PASSED — Phase 1 complete!")
        print("=" * 55)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Flask not running. Run: cd backend && flask run")
    except AssertionError as e:
        print(f"\nFAILED: {e}")
    except Exception as e:
        print(f"\nERROR: {e}")
        raise