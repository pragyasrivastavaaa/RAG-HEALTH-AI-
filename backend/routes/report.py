import json
from flask import Blueprint, request, jsonify
from database.db import query_db
from routes.auth import get_current_user

report_bp = Blueprint("report", __name__)


def safe_json(val):
    try:    return json.loads(val) if val else None
    except: return None


@report_bp.route("/reports", methods=["GET"])
def get_all_reports():
    """Returns only reports belonging to the logged-in user."""
    user = get_current_user(request)

    if user:
        # Logged in — show only this user's reports
        rows = query_db("""
            SELECT r.id, r.patient_name, r.filename, r.report_date,
                   r.uploaded_at, res.health_score
            FROM reports r
            LEFT JOIN results res ON res.report_id = r.id
            WHERE r.user_id = ?
            ORDER BY r.uploaded_at DESC
        """, (user["user_id"],))
    else:
        # Not logged in — return empty (frontend will redirect to login)
        rows = []

    return jsonify({"reports": [dict(row) for row in rows]}), 200


@report_bp.route("/report/<int:report_id>", methods=["GET"])
def get_report(report_id):
    """Returns a single report — only if it belongs to the logged-in user."""
    user = get_current_user(request)

    if user:
        row = query_db("""
            SELECT r.id, r.patient_name, r.filename, r.report_date,
                   r.uploaded_at, res.raw_values, res.interpretation,
                   res.diet_plan, res.rag_analysis, res.health_score
            FROM reports r
            LEFT JOIN results res ON res.report_id = r.id
            WHERE r.id = ? AND r.user_id = ?
        """, (report_id, user["user_id"]), one=True)
    else:
        row = query_db("""
            SELECT r.id, r.patient_name, r.filename, r.report_date,
                   r.uploaded_at, res.raw_values, res.interpretation,
                   res.diet_plan, res.rag_analysis, res.health_score
            FROM reports r
            LEFT JOIN results res ON res.report_id = r.id
            WHERE r.id = ?
        """, (report_id,), one=True)

    if row is None:
        return jsonify({"error": "Report not found"}), 404

    return jsonify({
        "id":             row["id"],
        "patient_name":   row["patient_name"],
        "filename":       row["filename"],
        "report_date":    row["report_date"],
        "uploaded_at":    row["uploaded_at"],
        "health_score":   row["health_score"],
        "raw_values":     safe_json(row["raw_values"]),
        "interpretation": safe_json(row["interpretation"]),
        "diet_plan":      safe_json(row["diet_plan"]),
        "rag_analysis":   safe_json(row["rag_analysis"])
    }), 200