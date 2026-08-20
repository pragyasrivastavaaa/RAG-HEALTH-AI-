"""
Phase 3 — Rule-Based Interpreter
Fixed health score: starts at 100, reasonable deductions per abnormal value.
"""
import json, os

RANGES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "normal_ranges.json")

CONDITION_MAP = {
    ("hemoglobin",        "Low"):  "anemia",
    ("glucose_fasting",   "High"): "diabetes_risk",
    ("glucose_pp",        "High"): "diabetes_risk",
    ("hba1c",             "High"): "prediabetes",
    ("cholesterol_total", "High"): "high_cholesterol",
    ("cholesterol_ldl",   "High"): "high_cholesterol",
    ("cholesterol_hdl",   "Low"):  "low_hdl",
    ("triglycerides",     "High"): "high_triglycerides",
    ("tsh",               "High"): "thyroid_high",
    ("tsh",               "Low"):  "thyroid_low",
    ("vitamin_d",         "Low"):  "vitamin_d_deficiency",
    ("vitamin_b12",       "Low"):  "vitamin_b12_deficiency",
    ("creatinine",        "High"): "high_creatinine",
    ("uric_acid",         "High"): "high_uric_acid",
    ("sgpt",              "High"): "high_liver_enzymes",
    ("sgot",              "High"): "high_liver_enzymes",
}

# Maximum deduction per parameter severity
DEDUCTIONS = {"mild": 4, "moderate": 8, "severe": 14}

# Maximum total deduction cap so score never goes below ~10 unreasonably
MAX_DEDUCTION = 85


def interpret(raw_values: dict):
    with open(RANGES_PATH) as f:
        ranges = json.load(f)

    findings   = []
    deductions = 0
    conditions = set()

    for key, value in raw_values.items():
        ref = ranges.get(key)
        if not ref:
            continue

        low, high   = ref["min"], ref["max"]
        display     = ref["display_name"]
        unit        = ref["unit"]

        if value < low:
            status   = "Low"
            severity = _severity(value, low)
        elif value > high:
            status   = "High"
            severity = _severity(value, high)
        else:
            status   = "Normal"
            severity = "none"

        cond = CONDITION_MAP.get((key, status))
        if cond:
            conditions.add(cond)

        deductions += DEDUCTIONS.get(severity, 0)

        findings.append({
            "key":        key,
            "display_name": display,
            "value":      value,
            "unit":       unit,
            "status":     status,
            "severity":   severity,
            "normal_min": low,
            "normal_max": high,
            "condition":  cond
        })

    # Cap deduction and compute score
    deductions = min(deductions, MAX_DEDUCTION)
    score      = max(15, 100 - deductions)

    return findings, score, list(conditions)


def _severity(value, boundary):
    if boundary == 0:
        return "mild"
    dev = abs(value - boundary) / abs(boundary) * 100
    return "mild" if dev <= 15 else "moderate" if dev <= 35 else "severe"