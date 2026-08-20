"""
RAG Engine - FAISS retrieval + LLM generation
"""
import os, sys, json, pickle, urllib.request, urllib.error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
from config import Config

_faiss_index = None
_faiss_meta  = None
_embed_model = None

GROQ_MODELS = ["llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]


def _load_vector_store():
    global _faiss_index, _faiss_meta, _embed_model
    if _faiss_index is not None:
        return True
    faiss_path = os.path.join(Config.VECTOR_STORE_DIR, "index.faiss")
    pkl_path   = os.path.join(Config.VECTOR_STORE_DIR, "index.pkl")
    if not os.path.exists(faiss_path):
        print("[RAG] Vector store not found. Run: python backend/modules/knowledge_builder.py")
        return False
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        _faiss_index = faiss.read_index(faiss_path)
        with open(pkl_path, "rb") as f:
            _faiss_meta = pickle.load(f)
        _embed_model = SentenceTransformer(_faiss_meta.get("model", "all-MiniLM-L6-v2"))
        print(f"[RAG] Loaded FAISS: {_faiss_index.ntotal} vectors")
        return True
    except Exception as e:
        print(f"[RAG] Load error: {e}")
        return False


def retrieve_context(query, top_k=5):
    if not _load_vector_store():
        return []
    try:
        import numpy as np
        vec = _embed_model.encode([query], convert_to_numpy=True).astype("float32")
        distances, indices = _faiss_index.search(vec, top_k)
        chunks  = _faiss_meta["chunks"]
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(chunks):
                results.append({"text": chunks[idx]["text"], "source": chunks[idx]["source"], "score": float(dist)})
        return results
    except Exception as e:
        print(f"[RAG] Retrieval error: {e}")
        return []


def build_rag_query(findings, conditions):
    abnormal = [f for f in findings if f["status"] != "Normal"]
    parts    = [f"{f['display_name']} {f['status'].lower()}" for f in abnormal[:6]]
    cond_str = " ".join(c.replace("_", " ") for c in conditions[:4])
    return f"{' '.join(parts)} {cond_str} diet lifestyle treatment".strip()


def build_prompt(patient_name, findings, conditions, health_score, retrieved_chunks):
    name     = patient_name if patient_name else "the patient"
    abnormal = [f for f in findings if f["status"] != "Normal"]
    findings_text = "; ".join(f"{f['display_name']}: {f['value']} {f['unit']} ({f['status']})" for f in abnormal[:3])
    # Shorter context - just key excerpts, not full chunks
    context_parts = []
    for c in retrieved_chunks[:2]:  # Limit to 2 chunks
        excerpt = c['text'][:200] + "..." if len(c['text']) > 200 else c['text']
        context_parts.append(f"• {excerpt}")
    context_text = "\n".join(context_parts)
    conds_str = ", ".join(c.replace("_", " ") for c in conditions[:2]) if conditions else "none"

    return f"""Health advisor for {name} (score: {health_score}/100).
Conditions: {conds_str}
Abnormal: {findings_text or "none"}

Medical context:
{context_text}

Provide brief analysis:
1. Health summary (1 sentence)
2. 2 diet tips
3. 2 lifestyle tips
4. When to see doctor

Keep concise."""


def call_groq(prompt):
    api_key = Config.GROQ_API_KEY
    if not api_key:
        return None
    # Try multiple models in order
    for model in GROQ_MODELS:
        payload = json.dumps({
            "model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600, "temperature": 0.4,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
                reply = data["choices"][0]["message"]["content"].strip()
                print(f"[RAG] Groq OK with model: {model}")
                return reply
        except urllib.error.HTTPError as e:
            print(f"[RAG] Groq {model} failed: {e.code}")
            if e.code == 401:
                print("[RAG] Invalid API key. Check your GROQ_API_KEY in .env")
                return None
            continue
        except Exception as e:
            print(f"[RAG] Groq error: {e}")
            continue
    return None


def call_ollama(prompt):
    print(f"[RAG] Ollama prompt length: {len(prompt)} characters")
    payload = json.dumps({"model": Config.OLLAMA_MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        f"{Config.OLLAMA_BASE_URL}/api/generate",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:  # Increased timeout for Ollama
            data = json.loads(resp.read().decode())
            return data.get("response", "").strip()
    except Exception as e:
        print(f"[RAG] Ollama error: {e}")
        return None


def call_llm(prompt):
    provider = Config.LLM_PROVIDER or "auto"
    print(f"[RAG] LLM provider configured: {provider}")

    if provider == "none":
        return None, None

    if provider == "ollama":
        result = call_ollama(prompt)
        return result, "ollama" if result else None

    if provider == "groq":
        result = call_groq(prompt)
        if result:
            return result, "groq"
        result = call_ollama(prompt)
        return result, "ollama" if result else None

    if Config.GROQ_API_KEY:
        result = call_groq(prompt)
        if result:
            return result, "groq"
        print("[RAG] Groq failed or unavailable, falling back to Ollama.")
    result = call_ollama(prompt)
    return result, "ollama" if result else None


def rule_based_summary(patient_name, findings, conditions, health_score):
    name     = patient_name or "there"
    abnormal = [f for f in findings if f["status"] != "Normal"]
    conds    = [c.replace("_", " ") for c in conditions[:3]]
    summary  = f"Hello {name}, your health score is {health_score}/100. "
    if not abnormal:
        summary += "All parameters are within normal range — great work!"
    else:
        summary += f"You have {len(abnormal)} abnormal parameters. "
        if conds:
            summary += f"Key conditions flagged: {', '.join(conds)}. "
        summary += "Please follow the diet and lifestyle recommendations below and consult your doctor."
    return summary


def generate_rag_analysis(patient_name, findings, conditions, health_score):
    query     = build_rag_query(findings, conditions)
    retrieved = retrieve_context(query, top_k=5)
    prompt    = build_prompt(patient_name, findings, conditions, health_score, retrieved)

    analysis, llm_source = call_llm(prompt)
    if not analysis:
        analysis   = rule_based_summary(patient_name, findings, conditions, health_score)
        llm_source = "fallback"

    sources = [{"source": c["source"], "excerpt": c["text"][:150]+"..."} for c in retrieved[:3]]
    return {"analysis": analysis, "sources": sources, "rag_used": len(retrieved) > 0,
            "llm_source": llm_source, "query_used": query}