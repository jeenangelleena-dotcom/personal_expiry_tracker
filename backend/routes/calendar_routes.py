import calendar
from datetime import date, datetime

from flask import Blueprint, render_template, request, session
from bson import ObjectId

from models.object_model import get_objects_by_user
from services.expiry_service import add_expiry_details
from utils.auth import login_required


calendar_bp = Blueprint(
    "calendar",
    __name__,
    url_prefix="/calendar"
)


@calendar_bp.route("/")
@login_required
def calendar_page():
    user_id = ObjectId(session["user_id"])

    # Get the same objects used by the dashboard
    objects = get_objects_by_user(user_id)

    # Use the same expiry calculation as the dashboard
    for item in objects:
        add_expiry_details(item)

    today = date.today()

    try:
        selected_year = int(
            request.args.get("year", today.year)
        )

        selected_month = int(
            request.args.get("month", today.month)
        )

    except ValueError:
        selected_year = today.year
        selected_month = today.month

    # Handle previous/next month
    if selected_month < 1:
        selected_month = 12
        selected_year -= 1

    if selected_month > 12:
        selected_month = 1
        selected_year += 1

    # Create calendar
    calendar_data = calendar.monthcalendar(
        selected_year,
        selected_month
    )

    # Store objects according to expiry date
    objects_by_date = {}

    for item in objects:

        expiry_date = item.get("expiry_date")

        if not expiry_date:
            continue

        try:
            expiry = datetime.strptime(
                expiry_date,
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):
            continue

        date_key = expiry.strftime("%Y-%m-%d")

        if date_key not in objects_by_date:
            objects_by_date[date_key] = []

        objects_by_date[date_key].append(item)

    # Previous month
    previous_month = selected_month - 1
    previous_year = selected_year

    if previous_month == 0:
        previous_month = 12
        previous_year -= 1

    # Next month
    next_month = selected_month + 1
    next_year = selected_year

    if next_month == 13:
        next_month = 1
        next_year += 1

    # ------------------------------------------------
    # SAME COUNTS AS DASHBOARD
    # ------------------------------------------------

    expired_count = 0
    today_count = 0
    expiring_soon_count = 0
    safe_count = 0

    for item in objects:

        days_remaining = item.get("days_remaining")

        if days_remaining is None:
            continue

        if days_remaining < 0:
            expired_count += 1

        elif days_remaining == 0:
            today_count += 1

        elif days_remaining <= 30:
            expiring_soon_count += 1

        else:
            safe_count += 1

    return render_template(
        "calendar.html",

        calendar_data=calendar_data,

        selected_year=selected_year,
        selected_month=selected_month,
        month_name=calendar.month_name[selected_month],

        previous_year=previous_year,
        previous_month=previous_month,

        next_year=next_year,
        next_month=next_month,

        objects=objects,
        objects_by_date=objects_by_date,

        today=today,

        # Dashboard-compatible counts
        expired_count=expired_count,
        today_count=today_count,
        expiring_soon_count=expiring_soon_count,
        safe_count=safe_count
    )