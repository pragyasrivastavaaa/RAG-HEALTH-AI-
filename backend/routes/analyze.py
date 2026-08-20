import json
from flask import Blueprint, request, jsonify
from database.db import query_db, insert_db, get_db
from modules.ocr_extractor import extract_text
from modules.nlp_parser import get_parsed_summary
from modules.name_extractor import extract_patient_name, extract_report_date, get_first_name
from modules.interpreter import interpret
from modules.recommender import recommend
from modules.rag_engine import generate_rag_analysis
from routes.auth import get_current_user

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/analyze/<int:report_id>", methods=["POST"])
def analyze_report(report_id):
    user = get_current_user(request)

    # Fetch report — if user logged in, verify ownership
    if user:
        report = query_db(
            "SELECT * FROM reports WHERE id=? AND (user_id=? OR user_id IS NULL)",
            (report_id, user["user_id"]), one=True
        )
    else:
        report = query_db("SELECT * FROM reports WHERE id=?", (report_id,), one=True)

    if not report:
        return jsonify({"error": f"Report {report_id} not found"}), 404

    # 1. Extract text
    try:
        raw_text = extract_text(report["file_path"])
    except FileNotFoundError:
        return jsonify({"error": "File not found on server"}), 404
    except Exception as e:
        return jsonify({"error": f"Extraction failed: {str(e)}"}), 500

    if not raw_text or len(raw_text.strip()) < 10:
        return jsonify({"error": "Could not extract readable text from this file."}), 422

    # 2. Extract metadata
    patient_name  = extract_patient_name(raw_text)
    patient_first = get_first_name(patient_name)
    report_date   = extract_report_date(raw_text)

    # 3. Parse lab values
    try:
        summary, raw_values = get_parsed_summary(raw_text)
    except Exception as e:
        return jsonify({"error": f"Parsing failed: {str(e)}"}), 500

    if not raw_values:
        return jsonify({
            "warning":      "No lab values detected in this report.",
            "patient_name": patient_name,
            "preview":      raw_text[:500]
        }), 200

    # 4. Interpret values (rule-based with fixed score)
    findings, health_score, conditions = interpret(raw_values)

    # 5. Diet + lifestyle recommendations
    diet_plan = recommend(conditions)

    # 6. RAG analysis
    rag_result = generate_rag_analysis(patient_name, findings, conditions, health_score)

    # 7. Update report metadata
    db = get_db()
    db.execute(
        "UPDATE reports SET patient_name=?, report_date=? WHERE id=?",
        (patient_name, report_date, report_id)
    )
    db.commit()

    # 8. Save results to DB
    raw_json  = json.dumps(raw_values)
    find_json = json.dumps(findings)
    diet_json = json.dumps(diet_plan)
    rag_json  = json.dumps(rag_result)

    existing = query_db("SELECT id FROM results WHERE report_id=?", (report_id,), one=True)
    if existing:
        db.execute("""UPDATE results
                      SET raw_values=?, interpretation=?, diet_plan=?, rag_analysis=?, health_score=?
                      WHERE report_id=?""",
                   (raw_json, find_json, diet_json, rag_json, health_score, report_id))
    else:
        insert_db("""INSERT INTO results
                     (report_id, raw_values, interpretation, diet_plan, rag_analysis, health_score)
                     VALUES (?,?,?,?,?,?)""",
                  (report_id, raw_json, find_json, diet_json, rag_json, health_score))
    db.commit()

    return jsonify({
        "message":          "Analysis complete",
        "report_id":        report_id,
        "filename":         report["filename"],
        "patient_name":     patient_name,
        "patient_first":    patient_first,
        "report_date":      report_date,
        "health_score":     health_score,
        "parameters_found": len(raw_values),
        "findings":         findings,
        "conditions":       conditions,
        "diet_plan":        diet_plan,
        "rag_analysis":     rag_result
    }), 200