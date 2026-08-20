"""
Phase 2 — Patient Name + Date Extractor
"""
import re


def extract_patient_name(raw_text: str) -> str | None:
    """Try to extract patient name from top of report."""
    text    = raw_text[:2000]
    patterns = [
        r"patient\s*(?:name)?\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})",
        r"name\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})",
        r"patient\s*[:\-]\s*([A-Za-z][A-Za-z\s\.]{2,40})",
        r"mr\.?\s+([A-Za-z][A-Za-z\s]{2,30})",
        r"mrs\.?\s+([A-Za-z][A-Za-z\s]{2,30})",
        r"ms\.?\s+([A-Za-z][A-Za-z\s]{2,30})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            name = re.split(
                r"\b(age|dob|date|sex|gender|ref|sample|report|ward|mob|phone)\b",
                name, flags=re.IGNORECASE
            )[0].strip()
            name = re.sub(r"\s+", " ", name)
            if 2 < len(name) < 50 and not any(c.isdigit() for c in name):
                return name.title()
    return None


def extract_report_date(raw_text: str) -> str | None:
    """Try to extract report date from text."""
    text     = raw_text[:2000]
    patterns = [
        r"(?:date|report\s*date|collected\s*on|sample\s*date)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})",
        r"(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def get_first_name(full_name: str | None) -> str | None:
    if not full_name:
        return None
    return full_name.strip().split()[0].title()