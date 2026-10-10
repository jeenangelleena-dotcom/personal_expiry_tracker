from flask import Flask, jsonify, render_template, session
from bson import ObjectId
from routes.upload_routes import upload_bp
from routes.calendar_routes import calendar_bp
from routes.report_routes import report_bp
from models.object_model import get_objects_by_user
from services.expiry_service import add_expiry_details
from utils.auth import login_required
from config import Config

from database.mongodb import (
    init_mongodb,
    get_database
)

from models.object_model import (
    get_objects_by_user
)

from routes.auth_routes import auth_bp
from routes.object_routes import object_bp

from services.expiry_service import (
    add_expiry_details
)

from services.scheduler_service import (
    start_scheduler,
    stop_scheduler
)

from utils.auth import login_required


# ==================================================
# FLASK APPLICATION
# ==================================================

app = Flask(__name__)

app.config.from_object(Config)

app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER


# ==================================================
# MONGODB
# ==================================================

init_mongodb(app)



app.register_blueprint(auth_bp)

app.register_blueprint(object_bp)

app.register_blueprint(upload_bp)

app.register_blueprint(calendar_bp)
app.register_blueprint(report_bp)
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

        return jsonify({
            "status": "error",
            "message": "MongoDB connection failed.",
            "error": str(error)
        }), 500


# ==================================================
# START AUTOMATIC REMINDER SCHEDULER
# ==================================================

start_scheduler(app)


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    try:

        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True,
            use_reloader=False
        )

    finally:

        stop_scheduler()