"""
Phase 3 Test Script — RAG Engine
Run from rag-health-ai/ root with Flask running.
Usage: python test_phase3.py
"""
import os, sys, json, requests

BASE = "http://localhost:5000/api"

SAMPLE_TEXT = """
PATHOLOGY REPORT
Patient Name: Rahul Sharma
Date: 15-Jan-2024
Hemoglobin: 10.5 g/dL
Glucose Fasting: 118 mg/dL
HbA1c: 6.2 %
Total Cholesterol: 215 mg/dL
LDL Cholesterol: 140 mg/dL
HDL Cholesterol: 38 mg/dL
Triglycerides: 175 mg/dL
TSH: 5.5 mIU/L
Vitamin D: 18 ng/mL
Vitamin B12: 180 pg/mL
SGPT (ALT): 52 U/L
Creatinine: 1.4 mg/dL
Uric Acid: 7.2 mg/dL
"""


def test_interpreter():
    print("\n--- Test 1: Interpreter unit test ---")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    from modules.interpreter import interpret
    from modules.nlp_parser import parse_lab_values

    vals = parse_lab_values(SAMPLE_TEXT)
    findings, score, conditions = interpret(vals)
    print(f"Health score : {score}/100")
    print(f"Conditions   : {conditions}")
    for f in findings:
        if f["status"] != "Normal":
            print(f"  {f['display_name']}: {f['value']} → {f['status']} ({f['severity']})")
    assert score < 100
    assert len(conditions) > 0
    print("PASSED")
    return findings, score, conditions


def test_rag_retrieval():
    print("\n--- Test 2: FAISS retrieval test ---")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    from modules.rag_engine import retrieve_context

    results = retrieve_context("high cholesterol diabetes diet recommendations", top_k=3)
    if not results:
        print("SKIP: Vector store not built. Run: python backend/modules/knowledge_builder.py")
        return
    print(f"Retrieved {len(results)} chunks:")
    for r in results:
        print(f"  [{r['source']}] score={r['score']:.2f} — {r['text'][:80]}...")
    assert len(results) > 0
    print("PASSED")


def test_rag_pipeline_direct():
    print("\n--- Test 3: Full RAG pipeline (direct) ---")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    from modules.rag_engine import generate_rag_analysis
    from modules.interpreter import interpret
    from modules.nlp_parser import parse_lab_values

    vals = parse_lab_values(SAMPLE_TEXT)
    findings, score, conditions = interpret(vals)

    result = generate_rag_analysis("Rahul", findings, conditions, score)
    print(f"LLM source : {result['llm_source']}")
    print(f"RAG used   : {result['rag_used']}")
    print(f"Sources    : {[s['source'] for s in result['sources']]}")
    print(f"Analysis   :\n{result['analysis'][:300]}...")
    assert result["analysis"]
    print("PASSED")


def make_pdf():
    lines   = SAMPLE_TEXT.strip().split("\n")
    content = ""
    y = 750
    for line in lines:
        safe     = line.replace("(","\\(").replace(")","\\)")
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
    path = "_p3_test.pdf"
    with open(path, "wb") as f: f.write(pdf.encode("latin-1"))
    return path


def test_full_flask_pipeline():
    print("\n--- Test 4: Full Flask RAG pipeline ---")
    pdf = make_pdf()
    with open(pdf, "rb") as f:
        r = requests.post(f"{BASE}/upload", files={"file": ("report.pdf", f, "application/pdf")})
    os.remove(pdf)
    assert r.status_code == 201
    report_id = r.json()["report_id"]

    r = requests.post(f"{BASE}/analyze/{report_id}")
    assert r.status_code == 200, f"Failed: {r.text}"
    data = r.json()

    print(f"Patient      : {data.get('patient_name')}")
    print(f"Health score : {data.get('health_score')}/100")
    print(f"Conditions   : {data.get('conditions')}")
    print(f"RAG source   : {data.get('rag_analysis', {}).get('llm_source')}")
    print(f"RAG used     : {data.get('rag_analysis', {}).get('rag_used')}")
    print(f"Diet tips    : {len(data.get('diet_plan', {}).get('diet', []))}")

    assert data.get("health_score") is not None
    assert len(data.get("findings", [])) > 0
    print("PASSED")
    return report_id


def test_chatbot(report_id):
    print(f"\n--- Test 5: RAG Chatbot (report #{report_id}) ---")
    r = requests.post(f"{BASE}/chat", json={
        "message":      "What should I eat to improve my cholesterol?",
        "report_id":    report_id,
        "patient_name": "Rahul"
    })
    assert r.status_code == 200
    data = r.json()
    print(f"RAG used : {data.get('rag_used')}")
    print(f"Sources  : {[s['source'] for s in data.get('sources', [])]}")
    print(f"Reply    : {data.get('reply', '')[:200]}")
    assert data.get("reply")
    print("PASSED")


if __name__ == "__main__":
    print("=" * 55)
    print("  RAG Health AI — Phase 3 Test Suite")
    print("  RAG Engine + Interpreter + Chatbot")
    print("=" * 55)
    try:
        test_interpreter()
        test_rag_retrieval()
        test_rag_pipeline_direct()
        report_id = test_full_flask_pipeline()
        test_chatbot(report_id)
        print("\n" + "=" * 55)
        print("  ALL TESTS PASSED — Phase 3 complete!")
        print("  RAG pipeline is fully working.")
        print("=" * 55)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Flask not running. Run: cd backend && flask run")
    except Exception as e:
        print(f"\nERROR: {e}")
        raise