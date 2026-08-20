"""
Phase 1 — Multimodal Input Extraction
======================================
Handles 3 types of input:
  1. Digital PDF    → PyMuPDF (fastest, no OCR needed)
  2. Image (JPG/PNG)→ Tesseract OCR
  3. Scanned PDF    → Convert pages to images → Tesseract OCR

The function auto-detects which path to use.
"""

import os
import fitz          # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

# ── Windows Tesseract path — uncomment and set if needed ──────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ── Minimum characters to consider digital extraction successful ──────────
MIN_TEXT_LENGTH = 80


def extract_text(file_path: str) -> str:
    """
    Main entry point. Auto-detects file type and extraction method.
    Returns raw text string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = file_path.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        return _extract_from_pdf(file_path)
    elif ext in ("jpg", "jpeg", "png"):
        return _extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def _extract_from_pdf(file_path: str) -> str:
    """
    Try digital text extraction first (PyMuPDF).
    If result is too short, fall back to OCR (scanned PDF).
    """
    digital_text = _digital_pdf_extract(file_path)

    if len(digital_text.strip()) >= MIN_TEXT_LENGTH:
        return digital_text.strip()

    # Fallback: scanned PDF → render each page as image → Tesseract
    print(f"[OCR] Digital extraction insufficient ({len(digital_text)} chars), running OCR...")
    return _scanned_pdf_extract(file_path).strip()


def _digital_pdf_extract(file_path: str) -> str:
    """Extract text from a digitally-created PDF using PyMuPDF."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page      = doc[page_num]
            page_text = page.get_text("text")          # plain text mode
            text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        doc.close()
    except Exception as e:
        raise RuntimeError(f"PyMuPDF extraction failed: {e}")
    return text


def _scanned_pdf_extract(file_path: str) -> str:
    """
    For scanned PDFs: render each page at 300 DPI → Tesseract OCR.
    300 DPI gives much better accuracy than lower resolutions.
    """
    text = ""
    temp_files = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat  = fitz.Matrix(300 / 72, 300 / 72)    # 300 DPI
            pix  = page.get_pixmap(matrix=mat, alpha=False)

            temp_path = f"_temp_page_{page_num}.png"
            pix.save(temp_path)
            temp_files.append(temp_path)

            img       = Image.open(temp_path)
            img       = _preprocess_image(img)
            page_text = pytesseract.image_to_string(
                img,
                config="--oem 3 --psm 6"
            )
            text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        doc.close()
    except Exception as e:
        raise RuntimeError(f"Scanned PDF OCR failed: {e}")
    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
    return text


def _extract_from_image(file_path: str) -> str:
    """
    Extract text from a JPG or PNG image using Tesseract.
    Applies preprocessing for better accuracy on medical reports.
    """
    try:
        img  = Image.open(file_path)
        img  = _preprocess_image(img)
        text = pytesseract.image_to_string(
            img,
            config="--oem 3 --psm 6"
        )
    except Exception as e:
        raise RuntimeError(f"Image OCR failed: {e}")
    return text.strip()


def _preprocess_image(img: Image.Image) -> Image.Image:
    """
    Preprocess image before OCR to improve accuracy:
    - Convert to grayscale
    - Increase contrast
    - Sharpen slightly
    These steps are especially helpful for printed/photographed reports.
    """
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    img = img.convert("L")                              # grayscale
    img = ImageEnhance.Contrast(img).enhance(2.0)       # boost contrast
    img = img.filter(ImageFilter.SHARPEN)               # sharpen text edges
    return img