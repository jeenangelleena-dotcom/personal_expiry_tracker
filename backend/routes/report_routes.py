from flask import Blueprint, Response, send_file

from services.report_service import (
    generate_csv,
    generate_pdf
)

from utils.auth import login_required


report_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@report_bp.route("/csv")
@login_required
def download_csv():

    csv_data = generate_csv()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=expiry_report.csv"
        }
    )


@report_bp.route("/pdf")
@login_required
def download_pdf():

    pdf_data = generate_pdf()

    return send_file(
        pdf_data,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="expiry_report.pdf"
    )