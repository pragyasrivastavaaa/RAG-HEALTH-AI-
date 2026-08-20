"""
Phase 6 — Extraction Accuracy Evaluation
Run: python evaluation/eval_extraction.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from modules.nlp_parser import parse_lab_values

GROUND_TRUTH = {
    "hemoglobin":        10.5,
    "glucose_fasting":   118.0,
    "glucose_pp":        165.0,
    "cholesterol_total": 215.0,
    "cholesterol_ldl":   140.0,
    "cholesterol_hdl":   38.0,
    "triglycerides":     175.0,
    "tsh":               5.5,
    "vitamin_d":         18.0,
    "vitamin_b12":       180.0,
    "creatinine":        1.4,
    "uric_acid":         7.2,
    "hba1c":             6.2,
}

SAMPLE_TEXT = """
PATHOLOGY REPORT
Patient Name: Rahul Sharma
Hemoglobin: 10.5 g/dL
Glucose Fasting: 118 mg/dL
Glucose PP: 165 mg/dL
Total Cholesterol: 215 mg/dL
LDL Cholesterol: 140 mg/dL
HDL Cholesterol: 38 mg/dL
Triglycerides: 175 mg/dL
TSH: 5.5 mIU/L
Vitamin D: 18 ng/mL
Vitamin B12: 180 pg/mL
Creatinine: 1.4 mg/dL
Uric Acid: 7.2 mg/dL
HbA1c: 6.2 %
"""


def evaluate():
    print("=" * 50)
    print("  Extraction Accuracy Evaluation")
    print("=" * 50)

    extracted = parse_lab_values(SAMPLE_TEXT)

    tp = fp = fn = 0
    print(f"\n{'Parameter':<25} {'Expected':>10} {'Extracted':>10} {'Match':>8}")
    print("-" * 55)

    for key, expected in GROUND_TRUTH.items():
        got = extracted.get(key)
        match = got is not None and abs(got - expected) < 0.01
        if match:     tp += 1
        elif got:     fp += 1
        else:         fn += 1
        status = "✓" if match else ("✗ wrong" if got else "✗ missing")
        print(f"{key:<25} {expected:>10} {str(got) if got else 'NOT FOUND':>10} {status:>8}")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"\nTrue Positives : {tp}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"Precision      : {precision:.2%}")
    print(f"Recall         : {recall:.2%}")
    print(f"F1 Score       : {f1:.2%}")
    print("=" * 50)


if __name__ == "__main__":
    evaluate()