import json
from flask import Blueprint, request, jsonify
from database.db import query_db
from modules.longitudinal import compute_longitudinal, get_longitudinal_rag_context
from routes.auth import get_current_user

longitudinal_bp = Blueprint("longitudinal", __name__)


@longitudinal_bp.route("/trends/<path:patient_name>", methods=["GET"])
def get_trends(patient_name):
    user = get_current_user(request)
    if user:
        rows = query_db("""
            SELECT r.id, r.patient_name, r.filename, r.uploaded_at,
                   res.raw_values, res.health_score
            FROM reports r LEFT JOIN results res ON res.report_id = r.id
            WHERE LOWER(r.patient_name) LIKE LOWER(?)
              AND (r.user_id = ? OR r.user_id IS NULL)
            ORDER BY r.uploaded_at ASC
        """, (f"%{patient_name.strip()}%", user["user_id"]))
    else:
        rows = query_db("""
            SELECT r.id, r.patient_name, r.filename, r.uploaded_at,
                   res.raw_values, res.health_score
            FROM reports r LEFT JOIN results res ON res.report_id = r.id
            WHERE LOWER(r.patient_name) LIKE LOWER(?)
            ORDER BY r.uploaded_at ASC
        """, (f"%{patient_name.strip()}%",))

    if not rows:
        return jsonify({"error": f"No reports found for '{patient_name}'", "total_reports": 0}), 404
    if len(rows) < 2:
        return jsonify({"message": "Only 1 report found. Upload more to see trends.", "total_reports": 1, "patient_name": rows[0]["patient_name"]}), 200

    all_results = []
    for row in rows:
        def sj(v):
            try: return json.loads(v) if v else {}
            except: return {}
        all_results.append({"report_id": row["id"], "filename": row["filename"], "uploaded_at": row["uploaded_at"], "raw_values": sj(row["raw_values"]), "health_score": row["health_score"] or 0})

    analysis = compute_longitudinal(all_results)
    rag_ctx  = get_longitudinal_rag_context(analysis)
    return jsonify({"patient_name": rows[0]["patient_name"], "total_reports": len(rows), "reports": [{"id": r["report_id"], "filename": r["filename"], "date": r["uploaded_at"], "health_score": r["health_score"]} for r in all_results], "longitudinal": analysis, "rag_context": rag_ctx}), 200


@longitudinal_bp.route("/trends/by-report/<int:report_id>", methods=["GET"])
def get_trends_by_report(report_id):
    report = query_db("SELECT patient_name FROM reports WHERE id=?", (report_id,), one=True)
    if not report or not report["patient_name"]:
        return jsonify({"error": "No patient name found"}), 404
    return get_trends(report["patient_name"])


@longitudinal_bp.route("/patients", methods=["GET"])
def list_patients():
    user = get_current_user(request)
    if user:
        rows = query_db("""SELECT patient_name, COUNT(*) as report_count, MAX(uploaded_at) as latest_upload FROM reports WHERE patient_name IS NOT NULL AND patient_name != '' AND (user_id=? OR user_id IS NULL) GROUP BY LOWER(patient_name) ORDER BY latest_upload DESC""", (user["user_id"],))
    else:
        rows = []
    return jsonify({"patients": [dict(row) for row in rows]}), 200