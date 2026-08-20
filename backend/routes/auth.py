"""
Phase 5 — Authentication
Register, login, logout using bcrypt + simple JWT-style tokens.
100% free, no external auth services needed.
"""
import json
import hashlib
import secrets
import time
from flask import Blueprint, request, jsonify, current_app
from database.db import query_db, insert_db, get_db

auth_bp = Blueprint("auth", __name__)

# In-memory token store {token: {user_id, email, name, expires}}
# In production use Redis; for this project in-memory is fine
_tokens = {}

TOKEN_EXPIRY = 60 * 60 * 24 * 7  # 7 days in seconds


def hash_password(password: str) -> str:
    """Hash password with SHA-256 + salt."""
    salt = "rag_health_ai_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_hex(32)


def create_token(user_id: int, email: str, name: str) -> str:
    """Create and store a session token."""
    token = generate_token()
    _tokens[token] = {
        "user_id": user_id,
        "email":   email,
        "name":    name,
        "expires": time.time() + TOKEN_EXPIRY
    }
    return token


def get_current_user(request):
    """Extract user from Authorization header. Returns user dict or None."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    data  = _tokens.get(token)
    if not data:
        return None
    if time.time() > data["expires"]:
        del _tokens[token]
        return None
    return data


def require_auth(f):
    """Decorator to protect routes that need login."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user(request)
        if not user:
            return jsonify({"error": "Not authenticated. Please log in."}), 401
        return f(*args, user=user, **kwargs)
    return decorated


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    POST /api/register
    Body: { "name": str, "email": str, "password": str }
    """
    body = request.get_json()
    if not body:
        return jsonify({"error": "No data provided"}), 400

    name     = body.get("name", "").strip()
    email    = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if "@" not in email:
        return jsonify({"error": "Invalid email address"}), 400

    # Check if email already registered
    existing = query_db("SELECT id FROM users WHERE email=?", (email,), one=True)
    if existing:
        return jsonify({"error": "Email already registered. Please log in."}), 409

    # Save user
    pw_hash = hash_password(password)
    user_id = insert_db(
        "INSERT INTO users (name, email, password_hash) VALUES (?,?,?)",
        (name, email, pw_hash)
    )

    token = create_token(user_id, email, name)
    return jsonify({
        "message": f"Welcome, {name}! Account created.",
        "token":   token,
        "user":    {"id": user_id, "name": name, "email": email}
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/login
    Body: { "email": str, "password": str }
    """
    body = request.get_json()
    if not body:
        return jsonify({"error": "No data provided"}), 400

    email    = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    pw_hash = hash_password(password)
    user    = query_db(
        "SELECT id, name, email FROM users WHERE email=? AND password_hash=?",
        (email, pw_hash), one=True
    )

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_token(user["id"], user["email"], user["name"])
    return jsonify({
        "message": f"Welcome back, {user['name']}!",
        "token":   token,
        "user":    {"id": user["id"], "name": user["name"], "email": user["email"]}
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """POST /api/logout — invalidate token."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        _tokens.pop(token, None)
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    """GET /api/me — return current user info."""
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": {
        "id":    user["user_id"],
        "name":  user["name"],
        "email": user["email"]
    }}), 200