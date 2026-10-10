import os

from flask import (
    Blueprint,
    send_from_directory,
    current_app
)

from utils.auth import login_required


upload_bp = Blueprint(
    "upload",
    __name__
)


@upload_bp.route(
    "/uploads/<path:filename>"
)
@login_required
def uploaded_file(filename):

    upload_folder = os.path.join(
        current_app.root_path,
        current_app.config["UPLOAD_FOLDER"]
    )

    return send_from_directory(
        upload_folder,
        filename
    )