"""
Phase 2 — NLP Parser
=====================
Extracts structured lab values from raw OCR text using:
  1. Regex patterns  (primary — fast, reliable for standard formats)
  2. spaCy NER       (secondary — helps with unusual formats)

Returns a clean dict like:
  { "hemoglobin": 11.2, "glucose_fasting": 118.0, ... }
"""

import re
import json
import os

RANGES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "normal_ranges.json"
)

# ── Regex patterns per parameter ─────────────────────────────────────────
# Each key maps to a list of patterns.
# First match wins for each key.
# Pattern captures ONE numeric group: the lab value.
PATTERNS = {
    "hemoglobin": [
        r"h(?:ae?moglobin|gb|b)[\s:=\-]+(\d+\.?\d*)",
        r"\bhb\b[\s:=]+(\d+\.?\d*)",
    ],
    "glucose_fasting": [
        r"(?:fasting\s+(?:blood\s+)?glucose|fbg|fbs|glucose\s*fasting|blood\s+sugar\s*fasting)[\s:=\-]+(\d+\.?\d*)",
    ],
    "glucose_pp": [
        r"(?:post\s*prandial|pp\s*bs?|2\s*hr?\s*pp|glucose\s*pp)[\s:=\-]+(\d+\.?\d*)",
    ],
    "cholesterol_total": [
        r"(?:total\s+)?cholesterol[\s:=\-]+(\d+\.?\d*)",
        r"t\.?\s*chol[\s:=\-]+(\d+\.?\d*)",
    ],
    "cholesterol_ldl": [
        r"ldl[\s\-:=]+(?:cholesterol[\s:=\-]+)?(\d+\.?\d*)",
        r"low\s+density\s+lipoprotein[\s:=\-]+(\d+\.?\d*)",
    ],
    "cholesterol_hdl": [
        r"hdl[\s\-:=]+(?:cholesterol[\s:=\-]+)?(\d+\.?\d*)",
        r"high\s+density\s+lipoprotein[\s:=\-]+(\d+\.?\d*)",
    ],
    "triglycerides": [
        r"triglycerides?[\s:=\-]+(\d+\.?\d*)",
        r"\btg\b[\s:=\-]+(\d+\.?\d*)",
    ],
    "tsh": [
        r"\btsh\b[\s:=\-]+(\d+\.?\d*)",
        r"thyroid\s+stimulating\s+hormone[\s:=\-]+(\d+\.?\d*)",
    ],
    "vitamin_d": [
        r"vitamin\s*d[\s\-:=]+(\d+\.?\d*)",
        r"25\s*(?:oh|hydroxy)[\s\-]*(?:vitamin\s*)?d[\s:=\-]+(\d+\.?\d*)",
        r"vit\.?\s*d[\s:=\-]+(\d+\.?\d*)",
    ],
    "vitamin_b12": [
        r"vitamin\s*b[\s\-]?12[\s:=\-]+(\d+\.?\d*)",
        r"vit\.?\s*b[\s\-]?12[\s:=\-]+(\d+\.?\d*)",
        r"cyanocobalamin[\s:=\-]+(\d+\.?\d*)",
    ],
    "creatinine": [
        r"s\.?\s*creatinine[\s:=\-]+(\d+\.?\d*)",
        r"creatinine[\s:=\-]+(\d+\.?\d*)",
    ],
    "uric_acid": [
        r"uric\s+acid[\s:=\-]+(\d+\.?\d*)",
        r"s\.?\s*uric[\s:=\-]+(\d+\.?\d*)",
    ],
    "wbc": [
        r"(?:wbc|white\s+blood\s+(?:cell|count))[\s:=\-]+(\d+\.?\d*)",
        r"(?:total\s+leukocyte|tlc)[\s:=\-]+(\d+\.?\d*)",
    ],
    "rbc": [
        r"(?:rbc|red\s+blood\s+(?:cell|count))[\s:=\-]+(\d+\.?\d*)",
    ],
    "platelets": [
        r"platelet[\s\w]*[\s:=\-]+(\d+\.?\d*)",
        r"\bplt\b[\s:=\-]+(\d+\.?\d*)",
    ],
    "hba1c": [
        r"hb\s*a1c[\s:=\-]+(\d+\.?\d*)",
        r"glycated\s+h(?:ae?moglobin)[\s:=\-]+(\d+\.?\d*)",
        r"glycosylated\s+hb[\s:=\-]+(\d+\.?\d*)",
    ],
    "sgpt": [
        r"(?:sgpt|alt|alanine\s+(?:amino)?transferase)[\s:=\-]+(\d+\.?\d*)",
    ],
    "sgot": [
        r"(?:sgot|ast|aspartate\s+(?:amino)?transferase)[\s:=\-]+(\d+\.?\d*)",
    ],
}


def load_normal_ranges():
    """Load reference ranges JSON."""
    with open(RANGES_PATH, "r") as f:
        return json.load(f)


def parse_lab_values(raw_text: str) -> dict:
    """
    Extract lab values from raw text using regex patterns.
    Returns dict of { parameter_key: float_value }.
    """
    # Normalise: lowercase, collapse whitespace
    text = raw_text.lower()
    text = re.sub(r"\s+", " ", text)

    found = {}
    for key, patterns in PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    found[key] = float(match.group(1))
                    break
                except ValueError:
                    continue
    return found


def get_parsed_summary(raw_text: str):
    """
    Full pipeline:
      1. Parse raw values
      2. Attach reference range + unit + display name

    Returns:
      summary  - list of dicts with full metadata (for display)
      raw_vals - plain dict (for DB storage + downstream use)
    """
    raw_vals = parse_lab_values(raw_text)
    ranges   = load_normal_ranges()
    summary  = []

    for key, value in raw_vals.items():
        ref = ranges.get(key, {})
        summary.append({
            "key":          key,
            "display_name": ref.get("display_name", key),
            "value":        value,
            "unit":         ref.get("unit", ""),
            "min":          ref.get("min"),
            "max":          ref.get("max"),
        })

    return summary, raw_vals