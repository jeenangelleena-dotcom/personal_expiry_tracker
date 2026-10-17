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
        current_app.config.get("UPLOAD_FOLDER", "uploads")
    )

    if os.path.exists(os.path.join(upload_folder, filename)):
        return send_from_directory(
            upload_folder,
            filename
        )

    tmp_folder = "/tmp/uploads"
    if os.path.exists(os.path.join(tmp_folder, filename)):
        return send_from_directory(
            tmp_folder,
            filename
        )

    return send_from_directory(
        upload_folder,
        filename
    )