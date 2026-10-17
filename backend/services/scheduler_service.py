import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from services.automatic_reminder_service import (
    process_automatic_reminders
)

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_reminder_job(app):
    """
    Execute reminder check inside Flask application context.
    """
    with app.app_context():
        try:
            result = process_automatic_reminders()
            print("----------------------------------------")
            print("Automatic reminder check completed.")
            print("Emails sent:", result["sent_count"])
            print("Emails failed:", result["failed_count"])
            print("----------------------------------------")
        except Exception as error:
            print("----------------------------------------")
            print("Automatic reminder check failed:", error)
            print("----------------------------------------")


def start_scheduler(app):
    """
    Start background APScheduler for local development only.
    Serverless environments like Vercel do not support persistent background
    threads; scheduled jobs in Vercel should use Vercel Crons (/api/cron/reminders).
    """
    if os.getenv("VERCEL") == "1":
        logger.info(
            "Vercel serverless environment detected: skipping APScheduler background thread. "
            "Use Vercel Crons pointing to /api/cron/reminders instead."
        )
        return

    if scheduler.running:
        return

    # Run initial check on local startup
    run_reminder_job(app)

    # Check every day at 9:00 AM in local mode
    scheduler.add_job(
        run_reminder_job,
        trigger="cron",
        hour=9,
        minute=0,
        args=[app],
        id="daily_expiry_reminder",
        replace_existing=True
    )

    scheduler.start()
    print("Automatic expiry reminder scheduler started.")
    print("Daily reminder check: 09:00 AM")


def stop_scheduler():
    """
    Safely stop background APScheduler if running.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Automatic expiry reminder scheduler stopped.")