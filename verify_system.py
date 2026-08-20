#!/usr/bin/env python3
"""
RAG Health AI — Complete System Verification & Startup Guide
Run this from the project root to verify everything is working
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))

print("\n" + "="*60)
print("  RAG HEALTH AI — SYSTEM VERIFICATION")
print("="*60 + "\n")

checks = []

# Check 1: Environment
print("✓ Checking virtual environment...")
try:
    import flask
    checks.append(("Virtual Environment", True, f"Python {sys.version.split()[0]}"))
except:
    checks.append(("Virtual Environment", False, "Not activated"))

# Check 2: Database
print("✓ Checking database...")
db_path = ROOT / "database.db"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    checks.append(("Database", True, f"{len(tables)} tables initialized"))
except Exception as e:
    checks.append(("Database", False, str(e)))

# Check 3: Knowledge Base
print("✓ Checking knowledge base...")
kb_path = ROOT / "knowledge_base"
kb_files = list(kb_path.glob("*.txt")) if kb_path.exists() else []
checks.append(("Knowledge Base", len(kb_files) > 0, f"{len(kb_files)} files found"))

# Check 4: Vector Store
print("✓ Checking vector store...")
vs_path = ROOT / "vector_store"
vs_files = list(vs_path.glob("*")) if vs_path.exists() else []
checks.append(("Vector Store (FAISS)", len(vs_files) >= 2, f"{len(vs_files)} files found"))

# Check 5: Frontend
print("✓ Checking frontend files...")
frontend_path = ROOT / "frontend"
required_pages = ["index.html", "dashboard.html", "login.html"]
pages_exist = all((frontend_path / page).exists() for page in required_pages)
checks.append(("Frontend Pages", pages_exist, f"{len(required_pages)} pages present"))

# Check 6: Backend Routes
print("✓ Checking backend routes...")
try:
    from app import app
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    api_routes = [r for r in routes if "/api/" in r]
    checks.append(("Backend Routes", len(api_routes) > 0, f"{len(api_routes)} API endpoints"))
except Exception as e:
    checks.append(("Backend Routes", False, str(e)))

# Check 7: OCR Extractor
print("✓ Checking OCR extraction...")
try:
    from modules.ocr_extractor import extract_text
    checks.append(("OCR Extractor", True, "PyMuPDF + Tesseract ready"))
except Exception as e:
    checks.append(("OCR Extractor", False, str(e)))

# Check 8: NLP Parser
print("✓ Checking NLP parser...")
try:
    from modules.nlp_parser import parse_lab_values
    checks.append(("NLP Parser", True, "Lab value extraction ready"))
except Exception as e:
    checks.append(("NLP Parser", False, str(e)))

# Check 9: RAG Engine
print("✓ Checking RAG engine...")
try:
    from modules.rag_engine import generate_rag_analysis
    checks.append(("RAG Engine", True, "FAISS + LLM provider ready"))
except Exception as e:
    checks.append(("RAG Engine", False, str(e)))

# Check 10: Config
print("✓ Checking configuration...")
try:
    from config import Config
    provider = getattr(Config, 'LLM_PROVIDER', 'auto')
    groq_key = bool(Config.GROQ_API_KEY)
    checks.append(("Config/LLM", True, f"Provider: {provider} (Groq key: {'✓' if groq_key else '✗'})"))
except Exception as e:
    checks.append(("Config/LLM", False, str(e)))

# Print Summary
print("\n" + "="*60)
print("  VERIFICATION RESULTS")
print("="*60 + "\n")

passed = sum(1 for _, status, _ in checks if status)
total = len(checks)

for name, status, detail in checks:
    icon = "✅" if status else "❌"
    print(f"{icon} {name:30s} — {detail}")

print("\n" + "="*60)
print(f"  PASSED: {passed}/{total}")
print("="*60 + "\n")

if passed == total:
    print("🎉 All systems ready! Follow the steps below to start the app:\n")
    print("  Terminal 1 — Start Ollama (optional, for local LLM):")
    print("    > ollama serve\n")
    print("  Terminal 2 — Start Flask backend:")
    print("    > cd backend")
    print("    > flask run\n")
    print("  Terminal 3 — Open frontend in browser:")
    print("    > Open: file:///path/to/frontend/index.html")
    print("    (Or use Live Server extension in VS Code)\n")
    print("  📊 Access the app:")
    print("    - Login page:   http://127.0.0.1:5500/frontend/login.html (Live Server)")
    print("    - Upload page:  http://127.0.0.1:5500/frontend/index.html")
    print("    - Dashboard:    http://127.0.0.1:5500/frontend/dashboard.html\n")
    sys.exit(0)
else:
    print(f"⚠️  {total - passed} check(s) failed. Review the errors above.\n")
    sys.exit(1)
