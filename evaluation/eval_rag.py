"""
Phase 6 — RAG Quality Evaluation
Measures how well the RAG engine retrieves relevant knowledge.
Run: python evaluation/eval_rag.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from modules.rag_engine import retrieve_context

TEST_QUERIES = [
    {"query": "high cholesterol diet treatment",          "expected_source": "diet_medical.txt"},
    {"query": "diabetes blood sugar management",          "expected_source": "who_guidelines.txt"},
    {"query": "vitamin d deficiency sunlight",            "expected_source": "diet_medical.txt"},
    {"query": "thyroid tsh hypothyroidism",               "expected_source": "who_guidelines.txt"},
    {"query": "preventive care lifestyle exercise",       "expected_source": "preventive_care.txt"},
    {"query": "anemia hemoglobin iron diet",              "expected_source": "diet_medical.txt"},
    {"query": "kidney creatinine uric acid gout",         "expected_source": "diet_medical.txt"},
    {"query": "liver enzymes sgpt sgot fatty liver",      "expected_source": "diet_medical.txt"},
]

def evaluate():
    print("=" * 55)
    print("  RAG Retrieval Quality Evaluation")
    print("=" * 55)

    hits = 0
    print(f"\n{'Query':<40} {'Expected':>20} {'Got':>20} {'Hit':>5}")
    print("-" * 85)

    for test in TEST_QUERIES:
        results = retrieve_context(test["query"], top_k=3)
        if not results:
            print(f"{test['query'][:38]:<40} {test['expected_source']:>20} {'NO RESULTS':>20} {'✗':>5}")
            continue
        top_source = results[0]["source"]
        hit        = any(r["source"] == test["expected_source"] for r in results)
        if hit: hits += 1
        print(f"{test['query'][:38]:<40} {test['expected_source']:>20} {top_source:>20} {'✓' if hit else '✗':>5}")

    precision = hits / len(TEST_QUERIES)
    print(f"\nRetrieval Precision@3 : {precision:.2%} ({hits}/{len(TEST_QUERIES)} queries hit expected source)")
    print("=" * 55)


if __name__ == "__main__":
    evaluate()