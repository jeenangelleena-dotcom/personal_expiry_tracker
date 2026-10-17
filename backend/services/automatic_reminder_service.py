from datetime import date, datetime
import logging
from bson import ObjectId

from database.mongodb import (
    get_objects_collection,
    get_users_collection
)

from services.reminder_service import (
    create_reminder
)

from services.email_service import (
    send_expiry_reminder
)

logger = logging.getLogger(__name__)


def should_send_reminder(object_data):
    """
    Decide whether an automatic reminder should be sent.

    A reminder is sent when:
    - The object has an expiry warning level.
    - A reminder has not already been sent for the
      current reminder level on the current date.
    """
    reminder = create_reminder(object_data)
    reminder_level = reminder.get("reminder_level")

    if reminder_level == "No Reminder":
        return False, reminder

    last_level = object_data.get("last_reminder_level")
    last_date = object_data.get("last_reminder_date")
    today = date.today().isoformat()

    # Do not send the same reminder repeatedly on the same day.
    if last_level == reminder_level and last_date == today:
        return False, reminder

    return True, reminder


def process_automatic_reminders():
    """
    Check all objects and automatically send
    expiry reminder emails to their owners.
    """
    objects_collection = get_objects_collection()
    users_collection = get_users_collection()

    objects = objects_collection.find({})

    sent_count = 0
    failed_count = 0

    for object_data in objects:
        should_send, reminder = should_send_reminder(object_data)

        if not should_send:
            continue

        user_id = object_data.get("user_id")
        if not user_id:
            continue

        try:
            user = users_collection.find_one({
                "_id": ObjectId(user_id)
            })
        except Exception:
            user = users_collection.find_one({
                "_id": user_id
            })

        if not user:
            continue

        user_email = user.get("email")
        if not user_email:
            continue

        object_name = (
            reminder.get("object_name")
            or object_data.get("name")
            or "Object"
        )

        result = send_expiry_reminder(
            user_email,
            object_name,
            reminder.get("days_remaining"),
            reminder.get("reminder_level")
        )

        is_success = (
            isinstance(result, dict) and result.get("status") == "success"
        ) or result is True

        if is_success:
            objects_collection.update_one(
                {
                    "_id": object_data["_id"]
                },
                {
                    "$set": {
                        "last_reminder_level": reminder["reminder_level"],
                        "last_reminder_date": date.today().isoformat(),
                        "last_reminder_sent_at": datetime.utcnow()
                    }
                }
            )
            sent_count += 1
        else:
            failed_count += 1
            err_msg = result.get("message") if isinstance(result, dict) else "Unknown error"
            logger.warning(
                "Failed to send reminder for %s to %s: %s",
                object_name,
                user_email,
                err_msg
            )

    return {
        "sent_count": sent_count,
        "failed_count": failed_count
    }