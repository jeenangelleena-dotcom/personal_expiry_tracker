from datetime import date, datetime


def calculate_days_remaining(expiry_date):
    """
    Calculate the number of days remaining
    until the expiry date.
    """

    if isinstance(expiry_date, datetime):
        expiry_date = expiry_date.date()

    elif isinstance(expiry_date, str):
        expiry_date = datetime.strptime(
            expiry_date,
            "%Y-%m-%d"
        ).date()

    today = date.today()

    return (expiry_date - today).days


def get_expiry_status(days_remaining):
    """
    Return the expiry status based on
    the number of days remaining.
    """

    if days_remaining < 0:
        return "Expired"

    if days_remaining == 0:
        return "Expires Today"

    if days_remaining <= 30:
        return "Expiring Soon"

    return "Safe"


def get_expiry_details(expiry_date):
    """
    Calculate both days remaining
    and expiry status.
    """

    days_remaining = calculate_days_remaining(
        expiry_date
    )

    status = get_expiry_status(
        days_remaining
    )

    return {
        "days_remaining": days_remaining,
        "status": status
    }


def add_expiry_details(object_data):
    """
    Add expiry information to an object.
    """

    expiry_date = object_data.get(
        "expiry_date"
    )

    if not expiry_date:
        object_data["days_remaining"] = None
        object_data["expiry_status"] = "Unknown"

        return object_data

    details = get_expiry_details(
        expiry_date
    )

    object_data["days_remaining"] = (
        details["days_remaining"]
    )

    object_data["expiry_status"] = (
        details["status"]
    )

    return object_data