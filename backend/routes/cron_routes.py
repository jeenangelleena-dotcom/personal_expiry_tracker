import os
import logging
from flask import Blueprint, jsonify, request
from services.automatic_reminder_service import process_automatic_reminders

logger = logging.getLogger(__name__)

cron_bp = Blueprint("cron", __name__, url_prefix="/api/cron")


@cron_bp.route("/reminders", methods=["GET", "POST"])
def run_reminders_cron():
    """
    Endpoint for scheduled expiry reminders on Vercel or external schedulers.
    Protected by CRON_SECRET if configured in environment variables.
    """
    cron_secret = os.getenv("CRON_SECRET", "").strip()

    if cron_secret:
        auth_header = request.headers.get("Authorization", "").strip()
        expected_bearer = f"Bearer {cron_secret}"
        query_key = request.args.get("key", "").strip()

        if auth_header != expected_bearer and query_key != cron_secret:
            logger.warning("Unauthorized cron reminder request attempt.")
            return jsonify({
                "status": "error",
                "message": "Unauthorized: invalid or missing cron secret."
            }), 401

    try:
        result = process_automatic_reminders()
        return jsonify({
            "status": "success",
            "message": "Automatic reminder check completed successfully.",
            "emails_sent": result.get("sent_count", 0),
            "emails_failed": result.get("failed_count", 0)
        }), 200

    except Exception as error:
        logger.error("Cron reminder check failed: %s", error)
        return jsonify({
            "status": "error",
            "message": "Reminder check failed.",
            "error": str(error)
        }), 500
