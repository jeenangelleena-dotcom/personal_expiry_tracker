import os
import sys
import logging

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, render_template, session
from bson import ObjectId

from config import Config
from database.mongodb import init_mongodb, get_database
from models.object_model import get_objects_by_user
from services.expiry_service import add_expiry_details
from services.scheduler_service import start_scheduler, stop_scheduler
from utils.auth import login_required

# Blueprints
from routes.auth_routes import auth_bp
from routes.object_routes import object_bp
from routes.upload_routes import upload_bp
from routes.calendar_routes import calendar_bp
from routes.report_routes import report_bp
from routes.cron_routes import cron_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================================================
# FLASK APPLICATION CREATION
# ==================================================

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config.from_object(Config)
app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER


# ==================================================
# MONGODB INITIALIZATION
# ==================================================

init_mongodb(app)


# ==================================================
# BLUEPRINT REGISTRATION
# ==================================================

app.register_blueprint(auth_bp)
app.register_blueprint(object_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(report_bp)
app.register_blueprint(cron_bp)


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():
    return render_template(
        "home.html"
    )


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = ObjectId(
        session["user_id"]
    )

    objects = get_objects_by_user(
        user_id
    )

    for item in objects:
        add_expiry_details(
            item
        )

    return render_template(
        "flask_dashboard.html",
        objects=objects
    )


# ==================================================
# HEALTH CHECK
# ==================================================

@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "success",
        "message": "Personal Expiry Tracker is running."
    })


# ==================================================
# DATABASE STATUS
# ==================================================

@app.route("/api/db-status")
def database_status():
    try:
        database = get_database()
        database.command("ping")

        return jsonify({
            "status": "success",
            "message": "MongoDB connection successful."
        })

    except Exception as error:
        logger.error("Database status check failed: %s", error)
        # Avoid leaking internal connection strings or credentials
        return jsonify({
            "status": "error",
            "message": "MongoDB connection check failed.",
            "error": "Could not connect to MongoDB database. Check server logs."
        }), 500


# ==================================================
# RUN APPLICATION (LOCAL DEVELOPMENT)
# ==================================================

if __name__ == "__main__":
    # Start scheduler only during local server execution
    start_scheduler(app)

    try:
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True,
            use_reloader=False
        )
    finally:
        stop_scheduler()