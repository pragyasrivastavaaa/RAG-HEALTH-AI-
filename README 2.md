# RAG Health AI

> A Multimodal Retrieval-Augmented Generative AI Framework for Longitudinal Lab Report Analysis

**Disclaimer: For informational purposes only. Always consult a qualified doctor.**

---

## 📋 Project Overview

**RAG Health AI** is an intelligent health analysis platform that combines **Retrieval-Augmented Generation (RAG)**, **Natural Language Processing (NLP)**, and **Machine Learning** to analyze blood test reports and medical documents. The system extracts lab values, provides evidence-based health insights from WHO guidelines, detects health conditions, and tracks longitudinal trends over time.

### Core Capabilities
- 📄 **Multi-format Document Processing**: Extracts text from PDFs (print & scanned images using OCR)
- 🔬 **Lab Value Parsing**: Automatically identifies and normalizes blood test results
- 🧠 **AI-Powered Analysis**: Uses RAG + LLM to interpret results against medical knowledge base
- 📊 **Health Scoring**: Calculates personalized health risk scores (0-100)
- 💊 **Smart Recommendations**: Provides diet, lifestyle, and preventive care suggestions
- 📈 **Longitudinal Tracking**: Analyzes health trends over multiple reports
- 💬 **Health Chatbot**: Interactive AI assistant for health-related questions
- 🔐 **User Authentication**: Secure login system with report history

---

## 🔄 System Workflow & Data Flow

### Complete User Journey (Flowchart)

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAG HEALTH AI WORKFLOW                       │
└─────────────────────────────────────────────────────────────────┘

1. USER AUTHENTICATION
   ┌──────────────┐
   │ User Login   │
   │  /Register   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────┐
   │ Session Token    │
   │ Authentication   │
   └──────┬───────────┘
          │
          ▼

2. DOCUMENT UPLOAD
   ┌──────────────┐
   │ Upload PDF   │
   │ (Blood Test) │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────────┐
   │ Validate File Type   │
   │ Store in /uploads/   │
   └──────┬───────────────┘
          │
          ▼

3. DOCUMENT PROCESSING
   ┌──────────────────────────┐
   │ OCR EXTRACTOR MODULE     │
   ├──────────────────────────┤
   │ • PyMuPDF extraction     │
   │ • Tesseract OCR (images) │
   │ • Text cleaning          │
   └──────┬───────────────────┘
          │
          ▼
   ┌──────────────────────────┐
   │ NAME EXTRACTOR MODULE    │
   ├──────────────────────────┤
   │ • Extract patient name   │
   │ • Extract test date      │
   └──────┬───────────────────┘
          │
          ▼

4. DATA EXTRACTION & PARSING
   ┌──────────────────────────┐
   │ NLP PARSER MODULE        │
   ├──────────────────────────┤
   │ • Regex-based extraction │
   │ • spaCy NER (entities)   │
   │ • Lab value detection    │
   │ • Unit normalization     │
   └──────┬───────────────────┘
          │
          │ Extracted Lab Values
          ▼
   ┌──────────────────────────┐
   │ Store in Database        │
   │ (SQLite)                 │
   └──────┬───────────────────┘
          │
          ▼

5. MULTI-PARALLEL ANALYSIS
   ┌──────────────────────────────────────────────────────┐
   │          PARALLEL PROCESSING PIPELINE               │
   ├──────────────────────────────────────────────────────┤
   │                                                      │
   │  Path A: RULE-BASED      Path B: RAG ANALYSIS      │
   │  ┌────────────────┐      ┌──────────────────────┐  │
   │  │ Interpreter    │      │ RAG Engine Module    │  │
   │  │ Module         │      │ ┌──────────────────┐ │  │
   │  ├────────────────┤      │ │1. Embed query    │ │  │
   │  │ • Normal range │      │ │2. FAISS search   │ │  │
   │  │   comparison   │      │ │3. Retrieve docs  │ │  │
   │  │ • Abnormality  │      │ │4. LLM synthesis  │ │  │
   │  │   detection    │      │ └──────────────────┘ │  │
   │  │ • Risk scoring │      │ Knowledge Base:      │  │
   │  │ • Condition    │      │ • WHO Guidelines     │  │
   │  │   identification      │ • Lab References    │  │
   │  └────────────────┘      │ • Diet Rules        │  │
   │                          │ • Preventive Care   │  │
   │                          └──────────────────────┘  │
   │                                                      │
   └───────────────┬──────────────────────────────────────┘
                  │
                  ▼

6. RECOMMENDATIONS ENGINE
   ┌──────────────────────────┐
   │ RECOMMENDER MODULE       │
   ├──────────────────────────┤
   │ • Diet recommendations   │
   │ • Lifestyle changes      │
   │ • Preventive measures    │
   │ • Follow-up tests        │
   └──────┬───────────────────┘
          │
          ▼

7. LONGITUDINAL ANALYSIS
   ┌──────────────────────────┐
   │ LONGITUDINAL MODULE      │
   ├──────────────────────────┤
   │ • Trend analysis         │
   │ • Health trajectory      │
   │ • Improvement/decline    │
   │ • Pattern detection      │
   └──────┬───────────────────┘
          │
          ▼

8. REPORT GENERATION
   ┌──────────────────────────┐
   │ CONSOLIDATED REPORT      │
   ├──────────────────────────┤
   │ • Health Score (0-100)   │
   │ • Lab Values + Status    │
   │ • Detected Conditions    │
   │ • Recommendations        │
   │ • RAG Insights           │
   │ • Trends (if available)  │
   └──────┬───────────────────┘
          │
          ▼

9. DASHBOARD & INTERACTION
   ┌──────────────────────────┐
   │ FRONTEND DASHBOARD       │
   ├──────────────────────────┤
   │ • Display Results        │
   │ • Health Score Visual    │
   │ • Lab Value Charts       │
   │ • AI Chatbot (Q&A)       │
   │ • Report History         │
   │ • Trend Visualizations   │
   └──────┬───────────────────┘
          │
          ▼
   ┌──────────────────────────┐
   │ USER VIEWS RESULTS       │
   │ & ENGAGES WITH CHATBOT   │
   └──────────────────────────┘
```

---

## 🏗️ System Architecture

### Technology Stack
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, CSS3, JavaScript | Web UI for upload, dashboard, chatbot |
| **Backend** | Flask (Python) | REST API server |
| **NLP** | spaCy, NLTK | Named entity recognition, text parsing |
| **OCR** | Tesseract, PyMuPDF | PDF & image text extraction |
| **Vector DB** | FAISS | Fast semantic search in knowledge base |
| **Embeddings** | HuggingFace Transformers | Text → vectors (sentence-transformers) |
| **LLM** | Ollama / Groq | AI inference for analysis synthesis |
| **Database** | SQLite | User data, report history, trends |
| **ML** | scikit-learn | Health scoring, prediction models |

### Module Responsibilities

| Module | Function | Input | Output |
|--------|----------|-------|--------|
| **ocr_extractor.py** | Extract text from PDFs (print + scanned) | PDF file | Raw text string |
| **name_extractor.py** | Extract patient info (name, date) | PDF text | Patient name, test date |
| **nlp_parser.py** | Parse lab values from text | Raw text | Structured lab values {name, value, unit, status} |
| **interpreter.py** | Rule-based health analysis | Lab values + normal ranges | Risk flags, condition detection |
| **rag_engine.py** | Semantic search + LLM synthesis | Lab values + context | AI-generated insights from knowledge base |
| **recommender.py** | Generate health recommendations | Analyzed values + conditions | Diet, lifestyle, preventive suggestions |
| **longitudinal.py** | Track trends across multiple reports | Historical lab data | Trend analysis, improvement metrics |
| **ml_predictor.py** | Predictive health scoring | Lab values + history | Health risk score (0-100) |

---

## 🔧 Key Features & Workflows

### Feature 1: Multi-Format Document Processing
```
PDF (Print or Scanned Image)
    ↓
ocr_extractor.py
├─ Types: PyMuPDF (text), Tesseract (images)
├─ Handles: Blurry scans, multiple pages, tables
└─ Output: Clean extracted text
```

### Feature 2: Intelligent Lab Value Extraction
```
Raw Text from PDF
    ↓
nlp_parser.py
├─ Regex patterns for common lab tests
├─ Unit normalization (mg/dL → mmol/L)
├─ Confidence scoring
└─ Output: {test_name, value, unit, reference_range, status}
```

### Feature 3: RAG-Powered AI Analysis
```
Extracted Lab Values
    ↓
rag_engine.py
├─ Step 1: Convert to semantic vectors
├─ Step 2: FAISS similarity search in knowledge base
│         (WHO guidelines, diet rules, preventive care)
├─ Step 3: LLM synthesis (Ollama or Groq)
├─ Step 4: Generate human-readable insights
└─ Output: AI-powered health analysis with citations
```

### Feature 4: Health Scoring System
```
Lab Values + Conditions Detected
    ↓
ml_predictor.py + interpreter.py
├─ Weighted risk scoring model
├─ Condition severity assessment
├─ Longitudinal deterioration detection
└─ Output: Health Score (0-100)
    └─ 0-30: High Risk ⚠️
    └─ 31-60: Moderate Risk ⚠️
    └─ 61-100: Healthy Status ✅
```

### Feature 5: Longitudinal Health Tracking
```
Multiple Reports Over Time
    ↓
longitudinal.py
├─ Compare lab values across reports
├─ Calculate trends (improving/declining)
├─ Detect patterns (e.g., rising cholesterol)
├─ Predictive analysis
└─ Output: Trend charts, health trajectory
```

### Feature 6: Conversational Chatbot
```
User Question + Report Context
    ↓
chat.py → rag_engine.py
├─ Embed question
├─ Retrieve relevant knowledge
├─ Generate contextual response
└─ Output: Health-related Q&A
```

---

## 📊 Data Storage & Flow

```
User Report Upload (PDF)
        ↓
├─ File Storage: /uploads/{user_id}/{filename}
├─ Database Entry: reports table
│   └─ Fields: id, user_id, filename, upload_date, status
│
Extraction Phase
        ↓
├─ Lab Values Table: lab_values
│   └─ Fields: test_name, value, unit, reference_min, reference_max
├─ Conditions Table: conditions_detected
│   └─ Fields: condition_name, severity, description
├─ Recommendations Table: recommendations
│   └─ Fields: type, category, description
│
Analysis Results
        ↓
└─ Report Summary: analysis_results
    └─ Fields: health_score, summary, rag_insights, timestamp
```

---

## Quick Start (Every Time You Open VS Code)

```bash
# Terminal 1 — start Ollama (optional, for local LLM)
ollama serve

# Terminal 2 — start Flask
cd backend
flask run

# Flask will auto-reload when you change files (development mode)
# Then open frontend/login.html with Live Server (right-click → Open with Live Server)

# If you want to skip GROQ, set `LLM_PROVIDER=ollama` in `.env` and run a local Ollama server.
```

```powershell
# Windows-friendly validation script
# Run from project root with the venv activated
python run_analysis_test.py
```

---

## First Time Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Mac/Linux

# 2. Install dependencies
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Build RAG knowledge base (run once)
cd ..
python backend/modules/knowledge_builder.py

# 4. Generate test PDF
python create_sample_report.py

# 5. Start Flask
cd backend
flask run
```

---

## Project Structure

```
rag-health-ai/
├── backend/
│   ├── app.py                    Flask entry point
│   ├── config.py                 Settings
│   ├── requirements.txt
│   ├── database/db.py            SQLite helpers
│   ├── routes/
│   │   ├── auth.py               Register, login, logout
│   │   ├── upload.py             POST /api/upload
│   │   ├── analyze.py            POST /api/analyze/:id
│   │   ├── report.py             GET /api/reports, /api/report/:id
│   │   ├── chat.py               POST /api/chat
│   │   └── longitudinal.py       GET /api/trends/:name
│   └── modules/
│       ├── ocr_extractor.py      PDF + image → text
│       ├── nlp_parser.py         text → lab values
│       ├── name_extractor.py     extract patient name
│       ├── interpreter.py        rule-based analysis
│       ├── recommender.py        diet + lifestyle tips
│       ├── rag_engine.py         FAISS + LLM pipeline
│       ├── longitudinal.py       trend analysis
│       └── knowledge_builder.py  build FAISS index
├── knowledge_base/               Medical knowledge docs
├── vector_store/                 FAISS index (auto-generated)
├── data/
│   ├── normal_ranges.json
│   └── diet_rules.json
├── frontend/
│   ├── login.html
│   ├── register.html
│   ├── index.html                Upload page
│   ├── dashboard.html            Results + chatbot
│   ├── history.html              Past reports
│   ├── trends.html               Longitudinal charts
│   ├── css/style.css
│   └── js/
│       ├── auth.js
│       ├── upload.js
│       ├── dashboard.js
│       ├── history.js
│       └── trends.js
├── evaluation/
│   ├── eval_extraction.py        Extraction accuracy
│   └── eval_rag.py               RAG retrieval quality
├── create_sample_report.py       Generate test PDF
└── .env                          API keys (never commit)
```

---

## 🎯 How to Use the Application

### 1. Register & Login
- Navigate to `frontend/login.html`
- Click "Register" for new account
- Enter username, password, email
- System creates secure session token

### 2. Upload Report
- Go to dashboard (`frontend/index.html`)
- Click "Select File" → Choose PDF (blood test report)
- **Supported formats**: 
  - Text-based PDFs (Lab reports, medical documents)
  - Scanned images (JPG, PNG, PDF with images)
- Click "Analyse Report"
- System processes file (typically 30-60 seconds)

### 3. View Results (Dashboard)
After analysis completes, see:
- **Health Score Card**: Overall risk assessment (0-100)
- **Lab Values Table**: All extracted values with status indicators
  - ✅ Normal (within reference range)
  - ⚠️ High/Low (outside range)
  - ℹ️ Reference ranges displayed
- **Detected Conditions**: Key health issues identified
- **RAG Insights**: Evidence-based recommendations from WHO guidelines
- **Personalized Recommendations**: Diet, lifestyle, follow-up tests
- **AI Chatbot**: Ask questions about your results

### 4. View History & Trends
- **History Tab**: All past reports with dates
- **Trends Tab**: Longitudinal analysis (if multiple reports)
  - Line charts showing lab value progression
  - Health score trajectory
  - Pattern detection (improving/declining trends)

### 5. Interactive Chatbot
- Ask health-related questions
- Examples:
  - "What does high cholesterol mean?"
  - "What should I eat to improve my test results?"
  - "Is my blood pressure getting worse?"
  - "What tests should I do next?"
- Bot provides context-aware answers from knowledge base

---

## 🔌 API Endpoints

### Authentication
```
POST /api/register
  Body: {username, email, password}
  Response: {user_id, token, message}

POST /api/login
  Body: {username, password}
  Response: {token, user_id, message}

POST /api/logout
  Headers: {Authorization: Bearer <token>}
  Response: {message: "Logged out"}
```

### Report Management
```
POST /api/upload
  Headers: {Authorization: Bearer <token>}
  Body: FormData(file: PDF)
  Response: {report_id, filename, status: "processing"}

GET /api/reports
  Headers: {Authorization: Bearer <token>}
  Response: [{id, filename, upload_date, health_score}, ...]

GET /api/report/:id
  Headers: {Authorization: Bearer <token>}
  Response: {
    id, user_id, filename, upload_date,
    health_score, lab_values, conditions, 
    recommendations, rag_insights
  }
```

### Analysis
```
POST /api/analyze/:id
  Headers: {Authorization: Bearer <token>}
  Response: {
    health_score, lab_values, conditions_detected,
    recommendations, rag_analysis, summary
  }

GET /api/trends/:test_name
  Headers: {Authorization: Bearer <token>}
  Response: [{date, value, unit, status}, ...]
```

### Chatbot
```
POST /api/chat
  Headers: {Authorization: Bearer <token>}
  Body: {question, report_id (optional), conversation_history}
  Response: {
    answer, context_used, confidence_score, 
    related_knowledge_sources
  }
```

---

## 🧪 Testing & Validation

### Run Test Suites
```bash
# Test Phase 1: Authentication & Database
python test_phase1.py

# Test Phase 2: Document Processing (OCR, Parsing)
python test_phase2.py

# Test Phase 3: Analysis Engine (Rules, RAG)
python test_phase3.py

# Test Phase 4: Longitudinal & Chatbot
python test_phase4.py

# Integration Test
python run_analysis_test.py
```

### Generate Sample Report
```bash
python create_sample_report.py
# Creates sample_blood_report.pdf with realistic lab values
```

### Evaluation Metrics
```bash
# Test extraction accuracy
python evaluation/eval_extraction.py
# Output: Precision, Recall, F1-score for each lab test

# Test RAG retrieval quality
python evaluation/eval_rag.py
# Output: Relevance scores, knowledge base coverage
```

### System Verification
```bash
python verify_system.py
# Checks: Python version, all dependencies, 
#         OCR setup, FAISS index, database schema
```

---

## 🔍 Troubleshooting

### Issue: "Module not found" errors
**Solution**: Ensure Flask is running from `/backend` directory with venv activated
```bash
cd backend
python app.py
```

### Issue: "FAISS index not found"
**Solution**: Build knowledge base (one-time setup)
```bash
cd backend
python modules/knowledge_builder.py
```

### Issue: OCR not extracting text from scanned PDFs
**Solution**: Install Tesseract
- **Windows**: Download from `github.com/UB-Mannheim/tesseract/wiki`
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### Issue: LLM responses are slow or timeout
**Solution**: Check which LLM provider is active
```bash
# In .env, try:
LLM_PROVIDER=ollama    # Faster, local
LLM_PROVIDER=groq      # Cloud-based, requires API key
LLM_PROVIDER=none      # Skip LLM (rule-based analysis only)
```

### Issue: Database locked error
**Solution**: Only one Flask instance should run at a time
```bash
# Kill any running Flask instances
Get-Process python | Stop-Process  # Windows
pkill flask                         # Mac/Linux
```

### Issue: Frontend not connecting to backend
**Solution**: Ensure backend is running and CORS is enabled
```bash
# Check Flask is running:
curl http://127.0.0.1:5000

# Should return: {"message": "RAG Health AI API running", "status": "ok"}
```

---

## Free API Keys (Optional)

| Service | URL | Use |
|---------|-----|-----|
| Ollama | ollama.com | Local offline LLM |
| HuggingFace | huggingface.co/settings/tokens | Embeddings |

Add to `.env`:
```
GROQ_API_KEY=your_key
HF_TOKEN=your_token
SECRET_KEY=any_random_string
LLM_PROVIDER=auto      # auto, ollama, groq, or none
```

If you do not want to use GROQ, set `LLM_PROVIDER=ollama` and start a local Ollama server with `ollama serve`.

---

## Running Evaluations (Phase 6)

```bash
python evaluation/eval_extraction.py
python evaluation/eval_rag.py
```

---

## 📈 Performance & Optimization

### Processing Speed
| Task | Time | Factors |
|------|------|---------|
| PDF Text Extraction | 2-5s | File size, image count |
| Lab Value Parsing | 1-2s | Text length, format complexity |
| RAG Search & Synthesis | 5-20s | LLM provider (Groq < Ollama) |
| Health Score Calculation | <1s | Number of values |
| **Total Per Report** | **30-60s** | System load, LLM availability |

### Optimization Tips
- Use **Groq API** (cloud) for faster LLM responses vs local Ollama
- Cache knowledge base embeddings (FAISS index)
- Run backend on machine with ≥8GB RAM
- Use SSD storage for faster PDF access

### Scalability Limitations
- **Current**: Single user, local processing
- **For Production**: 
  - Migrate to PostgreSQL (replace SQLite)
  - Add async task queue (Celery + Redis)
  - Implement load balancing (Gunicorn)
  - Use cloud LLM providers (Groq, OpenAI)

---

## 🚫 Limitations & Disclaimers

### Technical Limitations
- ❌ **Not for diagnosis**: This tool is for informational analysis only
- ❌ **Lab context**: Cannot distinguish (e.g., fasting vs non-fasting)
- ❌ **Medications**: Does not account for drug interactions
- ❌ **Edge cases**: May fail on unusual lab report formats
- ❌ **Language**: Currently supports English only

### Model Limitations
- RAG accuracy depends on knowledge base completeness
- LLM hallucination possible (especially with Ollama)
- Normal ranges vary by age, gender, pregnancy status
- Longitudinal analysis needs ≥2 reports for meaningful trends

### Legal & Ethical
- **Always consult doctors** for medical decisions
- System output should supplement, not replace, professional advice
- User data is stored locally (no cloud sync)
- No liability for health decisions based on this tool

---

## 🔮 Future Enhancements

### Phase 1: Enhanced Analysis
- [ ] Add medication interaction checker
- [ ] Support multiple languages (Spanish, Hindi, etc.)
- [ ] Gender & age-aware normal ranges
- [ ] Pregnancy/lactation-specific analysis
- [ ] Integration with wearable device data

### Phase 2: Advanced Features
- [ ] **Predictive Analytics**: Disease risk score (6-12 months)
- [ ] **Doctor Integration**: Share reports with healthcare providers
- [ ] **Mobile App**: React Native / Flutter for iOS & Android
- [ ] **Voice Input**: Speak health questions to chatbot
- [ ] **Report Comparison**: Side-by-side analysis of 2+ reports

### Phase 3: Enterprise Features
- [ ] **Multi-language Support**: Auto-translate knowledge base
- [ ] **Private Deployment**: Docker/Kubernetes for hospitals
- [ ] **API for Clinics**: White-label solution
- [ ] **Advanced Analytics**: Population health trends
- [ ] **Compliance**: HIPAA, GDPR, CCPA certifications

### Phase 4: ML Improvements
- [ ] **Custom Models**: Train on hospital-specific data
- [ ] **Federated Learning**: Learn without sharing patient data
- [ ] **Automatic Prompt Tuning**: Optimize LLM for accuracy
- [ ] **Explanation AI**: Show why health score changed

---

## 📚 Knowledge Base Sources

The system uses evidence-based medical knowledge from:

| Source | Content | Used For |
|--------|---------|----------|
| **WHO Guidelines** | Preventive care, disease management | Health recommendations |
| **Lab Reference Ranges** | Normal values by age/gender | Abnormality detection |
| **Nutrition Science** | Evidence-based diet advice | Diet recommendations |
| **Clinical Best Practices** | Standard medical protocols | Analysis framework |

**Note**: Knowledge base can be updated by editing files in `/knowledge_base/` and rebuilding FAISS index:
```bash
python backend/modules/knowledge_builder.py
```

---

## 🤝 Contributing

Found a bug or want to improve something?

1. **Report Issues**: Create detailed bug reports with:
   - Exact error message
   - Steps to reproduce
   - Environment (OS, Python version)
   - Sample PDF if applicable

2. **Submit Improvements**:
   - Fork repository
   - Create feature branch: `git checkout -b feature/your-feature`
   - Commit changes: `git commit -m "Add your feature"`
   - Push: `git push origin feature/your-feature`
   - Create Pull Request with description

3. **Areas for Help**:
   - Lab value extraction improvements
   - Knowledge base expansion
   - UI/UX enhancements
   - Performance optimization
   - Documentation & testing

---

## 📄 License & Attribution

- **Project**: RAG Health AI (Educational Use)
- **Framework**: Flask, FAISS, Ollama, HuggingFace
- **Data**: WHO, Medical Literature, Public Domain

**Recommendation**: Always validate results with qualified healthcare providers.

---

## 📧 Support & Questions

- **Documentation**: See STARTUP_GUIDE.md for setup help
- **Issues**: Check troubleshooting section above
- **Testing**: Run test suites to verify installation
- **Feedback**: Suggestions for improvements welcome

---

**Last Updated**: April 2026 | Version 5.0