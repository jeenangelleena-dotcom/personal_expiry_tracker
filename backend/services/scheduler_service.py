from apscheduler.schedulers.background import BackgroundScheduler

from services.automatic_reminder_service import (
    process_automatic_reminders
)


scheduler = BackgroundScheduler()


def run_reminder_job(app):

    with app.app_context():

        try:

            result = process_automatic_reminders()

            print("----------------------------------------")
            print("Automatic reminder check completed.")
            print(
                "Emails sent:",
                result["sent_count"]
            )
            print(
                "Emails failed:",
                result["failed_count"]
            )
            print("----------------------------------------")

        except Exception as error:

            print("----------------------------------------")
            print(
                "Automatic reminder check failed:",
                error
            )
            print("----------------------------------------")


def start_scheduler(app):

    if scheduler.running:
        return

    # Run once when Flask starts
    run_reminder_job(app)

    # FINAL VERSION:
    # Check every day at 9:00 AM
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

    print(
        "Automatic expiry reminder scheduler started."
    )

    print(
        "Daily reminder check: 09:00 AM"
    )


def stop_scheduler():

    if scheduler.running:

        scheduler.shutdown(
            wait=False
        )

        print(
            "Automatic expiry reminder scheduler stopped."
        )