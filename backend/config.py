import os
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    SECRET_KEY         = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    UPLOAD_FOLDER      = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
    DATABASE           = os.path.join(BASE_DIR, "database.db")
    KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base")
    VECTOR_STORE_DIR   = os.path.join(BASE_DIR, "vector_store")
    GROQ_API_KEY       = os.environ.get("GROQ_API_KEY", "")
    GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY", "")
    HF_TOKEN           = os.environ.get("HF_TOKEN", "")
    LLM_PROVIDER       = os.environ.get("LLM_PROVIDER", "auto").lower()
    OLLAMA_BASE_URL    = "http://localhost:11434"
    OLLAMA_MODEL       = "llama3.2"
    GROQ_MODEL         = "llama3-8b-8192"
    EMBEDDING_MODEL    = "all-MiniLM-L6-v2"