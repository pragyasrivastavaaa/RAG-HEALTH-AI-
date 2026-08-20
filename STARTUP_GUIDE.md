# RAG Health AI — Complete Setup & Startup Guide

## ✅ Prerequisites Installed

Your system has:
- ✅ Python 3.11 with venv
- ✅ PyMuPDF (PDF extraction)
- ✅ Tesseract OCR (scanned PDF OCR)
- ✅ FAISS (vector search)
- ✅ Ollama (optional local LLM) — llama3.2 (2GB)
- ✅ Knowledge base (WHO guidelines, diet rules)
- ✅ Vector store (FAISS index pre-built)
- ✅ Database (SQLite with schema)

---

## 🚀 How to Start the App

### Step 1: Verify the System

```powershell
cd C:\Users\bansa\OneDrive\Desktop\rag_health_ai
.\venv\Scripts\Activate.ps1
python verify_system.py
```

Expected output: ✅ All systems ready!

### Step 2: Start Ollama (Optional, Recommended)

Open a **NEW PowerShell terminal**:

```powershell
ollama serve
```

Expected output:
```
Listening on [::]:11434
```

Leave this running in the background.

### Step 3: Start Flask Backend

Open a **NEW PowerShell terminal**:

```powershell
cd C:\Users\bansa\OneDrive\Desktop\rag_health_ai
.\venv\Scripts\Activate.ps1
cd backend
flask run
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

Leave this running.

### Step 4: Open the Frontend

In your browser, open **one** of:
- `frontend/index.html` (from file system)
- `http://127.0.0.1:5500/frontend/index.html` (if using Live Server)

---

## 📋 Complete Workflow

1. **Upload Report**
   - Select a PDF (blood test report, or use `sample_blood_report.pdf`)
   - Click "Analyse Report"
   
2. **Analysis Runs**
   - PDF text extraction (PyMuPDF)
   - Lab value parsing (regex + spaCy)
   - RAG retrieval (FAISS vector search)
   - LLM analysis (Ollama or Groq)
   - Diet & lifestyle recommendations
   - Health score calculation
   
3. **Dashboard Shows Results**
   - Health score (0-100)
   - Lab values with status (Normal/High/Low)
   - Conditions detected
   - Diet and lifestyle recommendations
   - RAG analysis from WHO guidelines
   - Chat with healthbot

4. **View History & Trends**
   - Previous reports
   - Longitudinal health tracking
   - Trend charts

---

## 🔧 Configuration Options

### Use Ollama Only (No Groq)

Set in `.env`:
```
LLM_PROVIDER=ollama
```

### Use Groq API

Get free API key from: https://console.groq.com

Set in `.env`:
```
GROQ_API_KEY=your_api_key_here
LLM_PROVIDER=auto
```

### Disable LLM (Use Fallback Summary)

Set in `.env`:
```
LLM_PROVIDER=none
```

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to server"

**Solution:**
- Ensure Flask is running (see Step 3 above)
- Check terminal for Flask error messages
- Verify port 5000 is not in use

**Test:**
```powershell
# In a new terminal
curl http://127.0.0.1:5000/
```

Expected: `{"message":"RAG Health AI API running","status":"ok"}`

---

### Issue: Ollama Timeout

**Symptoms:**
- "Ollama error: timed out" in console
- Analysis completes but with fallback summary

**Solution 1:** 
Wait longer — Ollama's first request can take 30-90 seconds.

**Solution 2:**
Use smaller model:
```powershell
ollama pull llama2:7b
```

Set in `backend/config.py`:
```python
OLLAMA_MODEL = "llama2:7b"  # instead of "llama3.2"
```

**Solution 3:**
Skip Ollama altogether:
```
# In .env
LLM_PROVIDER=groq
GROQ_API_KEY=your_key
```

---

### Issue: "No lab values found in this file"

**Solution:**
- Use actual blood test reports (PDF or JPG)
- Or run: `python create_sample_report.py`
- Upload the generated `sample_blood_report.pdf`

---

### Issue: console logs disappear during upload

**Solution:**
In DevTools (F12), enable "Preserve log":
- Console tab → check "Preserve log" checkbox
- Now all logs stay visible even after page reload

---

### Issue: "Error: Analysis failed"

**Solution:**
1. Open DevTools (F12)
2. Go to Network tab
3. Click Analyze
4. Look for red errors in Network tab
5. Click the failed request to see the error detail

Common causes:
- Flask server crashed or not running
- Database locked (close other instances)
- Invalid PDF file

---

## 📊 Test the Backend Directly

```powershell
cd C:\Users\bansa\OneDrive\Desktop\rag_health_ai
python run_analysis_test.py
```

Expected output: Status 200 with full analysis JSON

---

## 📁 Project Structure

```
rag_health_ai/
├── backend/
│   ├── app.py                 ← Flask server
│   ├── config.py              ← Settings
│   ├── routes/                ← API endpoints
│   ├── modules/               ← AI components
│   └── database/              ← DB schema
├── frontend/
│   ├── index.html             ← Upload page
│   ├── dashboard.html         ← Results page
│   ├── login.html, register.html
│   ├── history.html, trends.html
│   ├── js/                    ← Frontend logic
│   └── css/                   ← Styling
├── knowledge_base/            ← WHO guidelines
├── vector_store/              ← FAISS index
├── uploads/                   ← Stored PDFs
├── database.db                ← SQLite file
├── .env                       ← API keys & config
├── verify_system.py           ← Verification tool
└── run_analysis_test.py       ← Backend test
```

---

## 🎯 Common Tasks

### Create Sample Blood Report
```powershell
python create_sample_report.py
```

### Run Tests
```powershell
# Phase 1-4 tests
python test_phase1.py
python test_phase2.py
python test_phase3.py
python test_phase4.py
```

### Rebuild Vector Store
```powershell
python backend/modules/knowledge_builder.py
```

### View Database Schema
```powershell
# Open database.db in any SQLite viewer
# Or use Python:
python -c "import sqlite3; c = sqlite3.connect('database.db'); c.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print([r[0] for r in c.fetchall()])"
```

---

## 📞 API Endpoints

All endpoints require `http://127.0.0.1:5000/api/`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/upload` | Upload PDF/image |
| POST | `/analyze/<id>` | Extract & analyze report |
| GET | `/report/<id>` | Get analysis results |
| GET | `/reports` | List all reports |
| POST | `/chat` | Chat with healthbot |
| GET | `/trends/<name>` | Longitudinal trends |

---

## ✨ Key Features

- 📄 **Multimodal Input**: PDF, JPG, PNG (auto-detects digital vs scanned)
- 🧠 **RAG Analysis**: Knowledge-grounded recommendations from WHO guidelines
- 📊 **Lab Value Parsing**: Regex + spaCy NER for accurate extraction
- 💬 **Health Chatbot**: Ask follow-up questions about your report
- 📈 **Longitudinal Tracking**: See health trends over time
- 🔐 **Optional Auth**: Login system available
- ⚡ **Fast**: FAISS vector search + local Ollama inference

---

## 🎓 Overview

The app is built in 6 phases:

1. **Phase 1** — PDF/image extraction (OCR + PyMuPDF)
2. **Phase 2** — Lab value parsing (regex patterns)
3. **Phase 3** — API & upload (Flask backend)
4. **Phase 4** — RAG analysis (FAISS + LLM)
5. **Phase 5** — Frontend (dashboard + charts)
6. **Phase 6** — Evaluation & optimization

All phases are implemented and integrated into one working system.

---

## 🚨 Emergency Restart

If something breaks:

```powershell
# Kill all Python processes
taskkill /IM python.exe /F

# Restart Flask
cd backend
flask run

# Restart Ollama (separate terminal)
ollama serve

# Refresh browser (Ctrl+Shift+R)
```

---

## ✅ Everything is Ready!

Your RAG Health AI project is **fully functional** and **production-ready**. Just run the 4 terminal commands above and start uploading reports.

**Questions?** Check the console logs (F12), network tab, and the troubleshooting section above.

---

**Last Updated:** April 14, 2026
**Version:** 5.0
**Status:** ✅ Production Ready
