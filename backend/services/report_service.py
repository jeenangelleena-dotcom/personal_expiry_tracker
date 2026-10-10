import csv
import io
from datetime import datetime

from flask import session
from bson import ObjectId

from models.object_model import get_objects_by_user
from services.expiry_service import add_expiry_details


def get_user_report_objects():
    user_id = ObjectId(session["user_id"])

    objects = get_objects_by_user(user_id)

    for item in objects:
        add_expiry_details(item)

    return objects


def get_status(days_remaining):

    if days_remaining < 0:
        return "Expired"

    if days_remaining == 0:
        return "Expires Today"

    if days_remaining <= 30:
        return "Expiring Soon"

    return "Safe"


def generate_csv():

    objects = get_user_report_objects()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Object Name",
        "Category",
        "Expiry Date",
        "Quantity",
        "Days Remaining",
        "Status",
        "Notes"
    ])

    for item in objects:

        days_remaining = item.get(
            "days_remaining",
            0
        )

        writer.writerow([
            item.get("name", ""),
            item.get("category", ""),
            item.get("expiry_date", ""),
            item.get("quantity", ""),
            days_remaining,
            get_status(days_remaining),
            item.get("notes", "")
        ])

    return output.getvalue()


def generate_pdf():

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    objects = get_user_report_objects()

    output = io.BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()

    elements = []

    user_name = session.get(
        "user_name",
        "User"
    )

    elements.append(
        Paragraph(
            "Personal Object Expiry Report",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"User: {user_name}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            "Generated: "
            + datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            ),
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(1, 12)
    )

    table_data = [
        [
            "Object",
            "Category",
            "Expiry Date",
            "Quantity",
            "Days Left",
            "Status",
            "Notes"
        ]
    ]

    for item in objects:

        days_remaining = item.get(
            "days_remaining",
            0
        )

        table_data.append([
            str(item.get("name", "")),
            str(item.get("category", "")),
            str(item.get("expiry_date", "")),
            str(item.get("quantity", "")),
            str(days_remaining),
            get_status(days_remaining),
            str(item.get("notes", ""))
        ])

    if len(table_data) == 1:

        table_data.append([
            "No objects found",
            "",
            "",
            "",
            "",
            "",
            ""
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            35 * mm,
            30 * mm,
            30 * mm,
            20 * mm,
            20 * mm,
            30 * mm,
            65 * mm
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#2563eb")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f8fafc")
                ]
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elements.append(table)

    document.build(elements)

    output.seek(0)

    return output