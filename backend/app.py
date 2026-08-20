import sys
import os

# This line MUST be first — adds backend/ to Python path
# so all modules.* and database.* imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from config import Config
from database.db import init_db
from routes.upload import upload_bp
from routes.report import report_bp
from routes.analyze import analyze_bp
from routes.chat import chat_bp
from routes.longitudinal import longitudinal_bp
from routes.auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(auth_bp,         url_prefix="/api")
app.register_blueprint(upload_bp,       url_prefix="/api")
app.register_blueprint(report_bp,       url_prefix="/api")
app.register_blueprint(analyze_bp,      url_prefix="/api")
app.register_blueprint(chat_bp,         url_prefix="/api")
app.register_blueprint(longitudinal_bp, url_prefix="/api")

with app.app_context():
    init_db()

@app.route("/")
def home():
    return {"message": "RAG Health AI API running", "status": "ok", "version": "5.0"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)