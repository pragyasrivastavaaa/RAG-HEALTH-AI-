"""Phase 3 — RAG Chatbot Route"""
import json
from flask import Blueprint, request, jsonify
from database.db import query_db
from modules.rag_engine import retrieve_context, call_groq, call_ollama, rule_based_summary

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    body = request.get_json()
    if not body or not body.get("message"):
        return jsonify({"error": "No message provided"}), 400

    message      = body.get("message", "").strip()
    report_id    = body.get("report_id")
    patient_name = body.get("patient_name")
    history      = body.get("history", [])

    # Load report context from DB
    findings, conditions, health_score, diet_plan = [], [], 0, {}
    if report_id:
        row = query_db("""SELECT res.interpretation, res.diet_plan, res.health_score
                          FROM results res WHERE res.report_id=?""", (report_id,), one=True)
        if row:
            def sj(v): 
                try: return json.loads(v) if v else []
                except: return []
            findings     = sj(row["interpretation"])
            diet_plan    = sj(row["diet_plan"]) if row["diet_plan"] else {}
            health_score = row["health_score"] or 0
            conditions   = list({f["condition"] for f in findings if f.get("condition")})

    # Retrieve relevant medical knowledge for the question
    retrieved = retrieve_context(message + " " + " ".join(conditions[:3]), top_k=3)
    context   = "\n".join(c["text"][:200] for c in retrieved)

    name  = patient_name or "there"
    abnormal = [f for f in findings if f.get("status") != "Normal"]
    findings_str = ", ".join(f"{f['display_name']}: {f['value']} ({f['status']})" for f in abnormal[:5])

    system = f"""You are a health assistant for {name}.
Their health score is {health_score}/100.
Abnormal values: {findings_str or 'none'}
Conditions: {', '.join(c.replace('_',' ') for c in conditions) or 'none'}

Relevant medical knowledge:
{context}

Answer the question concisely in 2-4 sentences. Be warm and supportive.
Always suggest consulting a doctor for medical decisions."""

    prompt = f"{system}\n\nQuestion: {message}"

    reply = call_groq(prompt) or call_ollama(prompt)
    if not reply:
        reply = rule_based_summary(patient_name, findings, conditions, health_score)

    sources = [{"source": c["source"], "excerpt": c["text"][:100]+"..."} for c in retrieved[:2]]

    return jsonify({
        "reply":   reply,
        "sources": sources,
        "rag_used": len(retrieved) > 0
    }), 200