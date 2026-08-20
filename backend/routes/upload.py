import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from database.db import insert_db
from routes.auth import get_current_user

upload_bp = Blueprint("upload", __name__)


def allowed_file(filename):
    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def safe_filename(original_name):
    ext = original_name.rsplit(".", 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file in request"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF, JPG, PNG allowed"}), 400

    # Get logged-in user (optional — works without login too)
    user    = get_current_user(request)
    user_id = user["user_id"] if user else None

    saved_name = safe_filename(file.filename)
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file_path  = os.path.join(upload_dir, saved_name)
    file.save(file_path)

    report_id = insert_db(
        "INSERT INTO reports (user_id, filename, file_path) VALUES (?,?,?)",
        (user_id, file.filename, file_path)
    )

    return jsonify({
        "message":   "File uploaded successfully",
        "report_id": report_id,
        "filename":  file.filename,
        "saved_as":  saved_name
    }), 201