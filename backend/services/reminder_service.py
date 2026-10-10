from datetime import date, datetime


def get_reminder_level(days_remaining):
    """
    Determine the automatic reminder level.
    """

    if days_remaining < 0:
        return "Expired"

    if days_remaining == 0:
        return "Expires Today"

    if days_remaining == 7:
        return "Urgent"

    if days_remaining == 30:
        return "Upcoming"

    return "No Reminder"


def create_reminder(object_data):
    """
    Create an automatic reminder for an object.
    """

    expiry_date = object_data.get("expiry_date")

    if not expiry_date:
        return {
            "reminder_level": "No Reminder",
            "message": "Expiry date is not available.",
            "days_remaining": None,
            "object_name": object_data.get(
                "name",
                "Object"
            )
        }

    if isinstance(expiry_date, str):
        expiry_date = datetime.strptime(
            expiry_date,
            "%Y-%m-%d"
        ).date()

    elif isinstance(expiry_date, datetime):
        expiry_date = expiry_date.date()

    elif not isinstance(expiry_date, date):
        return {
            "reminder_level": "No Reminder",
            "message": "Invalid expiry date.",
            "days_remaining": None,
            "object_name": object_data.get(
                "name",
                "Object"
            )
        }

    days_remaining = (
        expiry_date - date.today()
    ).days

    reminder_level = get_reminder_level(
        days_remaining
    )

    object_name = object_data.get(
        "name",
        "Object"
    )

    if reminder_level == "Expired":

        message = (
            f"{object_name} has already expired."
        )

    elif reminder_level == "Expires Today":

        message = (
            f"{object_name} expires today."
        )

    elif reminder_level == "Urgent":

        message = (
            f"{object_name} expires in "
            f"{days_remaining} day(s)."
        )

    elif reminder_level == "Upcoming":

        message = (
            f"{object_name} will expire in "
            f"{days_remaining} day(s)."
        )

    else:

        message = (
            f"{object_name} does not require "
            "a reminder yet."
        )

    return {
        "reminder_level": reminder_level,
        "days_remaining": days_remaining,
        "message": message,
        "object_name": object_name
    }


def get_reminders(objects):
    """
    Return objects that currently require
    an automatic reminder.
    """

    reminders = []

    for object_data in objects:

        reminder = create_reminder(
            object_data
        )

        if (
            reminder["reminder_level"]
            != "No Reminder"
        ):

            reminder["object_id"] = str(
                object_data.get("_id", "")
            )

            reminders.append(reminder)

    return reminders