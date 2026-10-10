import os
from datetime import datetime

from bson import ObjectId

from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    current_app,
    render_template,
    redirect,
    url_for,
    flash
)

from werkzeug.utils import secure_filename

from models.object_model import (
    create_object,
    get_objects_by_user,
    get_object_by_id,
    update_object,
    delete_object
)

from services.expiry_service import add_expiry_details

from utils.auth import login_required


object_bp = Blueprint(
    "objects",
    __name__,
    url_prefix="/api/objects"
)
def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in current_app.config[
        "ALLOWED_IMAGE_EXTENSIONS"
    ]

@object_bp.route(
    "/add",
    methods=["GET"]
)
@login_required
def add_object_page():

    return render_template(
        "add_object.html"
    )


# ==================================================
# STORED OBJECTS PAGE
# ==================================================

@object_bp.route(
    "/page",
    methods=["GET"]
)
@login_required
def objects_page():

    user_id = ObjectId(
        session["user_id"]
    )

    objects = get_objects_by_user(
        user_id
    )

    for item in objects:

        add_expiry_details(
            item
        )

    return render_template(
        "flask_objects.html",
        objects=objects
    )


# ==================================================
# CREATE OBJECT FROM WEBSITE
# ==================================================

@object_bp.route(
    "/page/create",
    methods=["POST"]
)
@login_required
def create_object_page():

    name = request.form.get(
        "name",
        ""
    ).strip()

    category = request.form.get(
        "category",
        ""
    ).strip()

    expiry_date = request.form.get(
        "expiry_date",
        ""
    ).strip()

    quantity = request.form.get(
        "quantity",
        "1"
    ).strip()

    notes = request.form.get(
        "notes",
        ""
    ).strip()


    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    if not name:

        flash(
            "Object name is required.",
            "error"
        )

        return redirect(
            url_for(
                "objects.add_object_page"
            )
        )


    if not category:

        flash(
            "Category is required.",
            "error"
        )

        return redirect(
            url_for(
                "objects.add_object_page"
            )
        )


    if not expiry_date:

        flash(
            "Expiry date is required.",
            "error"
        )

        return redirect(
            url_for(
                "objects.add_object_page"
            )
        )


    try:

        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError

    except ValueError:

        flash(
            "Quantity must be a positive number.",
            "error"
        )

        return redirect(
            url_for(
                "objects.add_object_page"
            )
        )


    try:

        datetime.strptime(
            expiry_date,
            "%Y-%m-%d"
        )

    except ValueError:

        flash(
            "Invalid expiry date.",
            "error"
        )

        return redirect(
            url_for(
                "objects.add_object_page"
            )
        )


    # --------------------------------------------------
    # IMAGE UPLOAD
    # --------------------------------------------------

    image_filename = None


    if "image" in request.files:

        image = request.files["image"]


        if image.filename:

            if not allowed_file(
                image.filename
            ):

                flash(
                    "Invalid image format. "
                    "Use PNG, JPG, JPEG or WEBP.",
                    "error"
                )

                return redirect(
                    url_for(
                        "objects.add_object_page"
                    )
                )


            image_filename = secure_filename(
                image.filename
            )


            upload_folder = os.path.join(
                current_app.root_path,
                current_app.config[
                    "UPLOAD_FOLDER"
                ]
            )


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            image_path = os.path.join(
                upload_folder,
                image_filename
            )


            image.save(
                image_path
            )


    # --------------------------------------------------
    # OBJECT DATA
    # --------------------------------------------------

    object_data = {

        "user_id": ObjectId(
            session["user_id"]
        ),

        "name": name,

        "category": category,

        "expiry_date": expiry_date,

        "quantity": quantity,

        "notes": notes,

        "image": image_filename,

        "created_at": datetime.utcnow(),

        "updated_at": datetime.utcnow(),

        # Automatic reminder history
        "last_reminder_level": None,

        "last_reminder_date": None,

        "last_reminder_sent_at": None
    }


    create_object(
        object_data
    )


    flash(
        "Object added successfully.",
        "success"
    )


    return redirect(
        url_for(
            "objects.objects_page"
        )
    )


# ==================================================
# DELETE OBJECT FROM WEBSITE
# ==================================================

@object_bp.route(
    "/page/delete/<object_id>",
    methods=["POST"]
)
@login_required
def delete_object_page(
    object_id
):

    try:

        object_id = ObjectId(
            object_id
        )

    except Exception:

        flash(
            "Invalid object ID.",
            "error"
        )

        return redirect(
            url_for(
                "objects.objects_page"
            )
        )


    item = get_object_by_id(
        object_id
    )


    if not item:

        flash(
            "Object not found.",
            "error"
        )

        return redirect(
            url_for(
                "objects.objects_page"
            )
        )


    if (
        str(item["user_id"])
        != session["user_id"]
    ):

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for(
                "objects.objects_page"
            )
        )


    # --------------------------------------------------
    # DELETE UPLOADED IMAGE
    # --------------------------------------------------

    image_filename = item.get(
        "image"
    )


    if image_filename:

        upload_folder = os.path.join(
            current_app.root_path,
            current_app.config[
                "UPLOAD_FOLDER"
            ]
        )


        image_path = os.path.join(
            upload_folder,
            image_filename
        )


        if os.path.exists(
            image_path
        ):

            os.remove(
                image_path
            )


    delete_object(
        object_id
    )


    flash(
        "Object deleted successfully.",
        "success"
    )


    return redirect(
        url_for(
            "objects.objects_page"
        )
    )


# ==================================================
# API ROUTES
# ==================================================


# ==================================================
# ADD OBJECT API
# ==================================================

@object_bp.route(
    "",
    methods=["POST"]
)
@login_required
def add_object():

    name = request.form.get(
        "name",
        ""
    ).strip()

    category = request.form.get(
        "category",
        ""
    ).strip()

    expiry_date = request.form.get(
        "expiry_date",
        ""
    ).strip()

    quantity = request.form.get(
        "quantity",
        "1"
    ).strip()

    notes = request.form.get(
        "notes",
        ""
    ).strip()


    if not name:

        return jsonify({
            "status": "error",
            "message": "Object name is required"
        }), 400


    if not category:

        return jsonify({
            "status": "error",
            "message": "Category is required"
        }), 400


    if not expiry_date:

        return jsonify({
            "status": "error",
            "message": "Expiry date is required"
        }), 400


    try:

        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError

    except ValueError:

        return jsonify({
            "status": "error",
            "message": "Quantity must be a positive number"
        }), 400


    try:

        datetime.strptime(
            expiry_date,
            "%Y-%m-%d"
        )

    except ValueError:

        return jsonify({
            "status": "error",
            "message": "Invalid expiry date"
        }), 400


    image_filename = None


    if "image" in request.files:

        image = request.files["image"]


        if image.filename:

            if not allowed_file(
                image.filename
            ):

                return jsonify({
                    "status": "error",
                    "message": "Invalid image type"
                }), 400


            image_filename = secure_filename(
                image.filename
            )


            upload_folder = os.path.join(
                current_app.root_path,
                current_app.config[
                    "UPLOAD_FOLDER"
                ]
            )


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            image.save(
                os.path.join(
                    upload_folder,
                    image_filename
                )
            )


    object_data = {

        "user_id": ObjectId(
            session["user_id"]
        ),

        "name": name,

        "category": category,

        "expiry_date": expiry_date,

        "quantity": quantity,

        "notes": notes,

        "image": image_filename,

        "created_at": datetime.utcnow(),

        "updated_at": datetime.utcnow(),

        "last_reminder_level": None,

        "last_reminder_date": None,

        "last_reminder_sent_at": None
    }


    object_id = create_object(
        object_data
    )


    return jsonify({

        "status": "success",

        "message": "Object added successfully",

        "object_id": str(
            object_id
        )

    }), 201


# ==================================================
# GET ALL OBJECTS
# ==================================================

@object_bp.route(
    "",
    methods=["GET"]
)
@login_required
def get_objects():

    user_id = ObjectId(
        session["user_id"]
    )


    objects = get_objects_by_user(
        user_id
    )


    object_list = []


    for item in objects:

        # ------------------------------------------
        # AUTOMATIC EXPIRY CALCULATION
        # ------------------------------------------

        add_expiry_details(
            item
        )


        # ------------------------------------------
        # CONVERT MONGODB VALUES
        # ------------------------------------------

        item["_id"] = str(
            item["_id"]
        )


        item["user_id"] = str(
            item["user_id"]
        )


        if "created_at" in item:

            item["created_at"] = (
                item["created_at"]
                .isoformat()
            )


        if "updated_at" in item:

            item["updated_at"] = (
                item["updated_at"]
                .isoformat()
            )


        object_list.append(
            item
        )


    return jsonify({

        "status": "success",

        "count": len(
            object_list
        ),

        "objects": object_list

    }), 200


# ==================================================
# GET SINGLE OBJECT
# ==================================================

@object_bp.route(
    "/<object_id>",
    methods=["GET"]
)
@login_required
def get_single_object(
    object_id
):

    try:

        object_id = ObjectId(
            object_id
        )

    except Exception:

        return jsonify({
            "status": "error",
            "message": "Invalid object ID"
        }), 400


    item = get_object_by_id(
        object_id
    )


    if not item:

        return jsonify({
            "status": "error",
            "message": "Object not found"
        }), 404


    if (
        str(item["user_id"])
        != session["user_id"]
    ):

        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403


    add_expiry_details(
        item
    )


    item["_id"] = str(
        item["_id"]
    )


    item["user_id"] = str(
        item["user_id"]
    )


    if "created_at" in item:

        item["created_at"] = (
            item["created_at"]
            .isoformat()
        )


    if "updated_at" in item:

        item["updated_at"] = (
            item["updated_at"]
            .isoformat()
        )


    return jsonify({

        "status": "success",

        "object": item

    }), 200


# ==================================================
# UPDATE OBJECT
# ==================================================

@object_bp.route(
    "/<object_id>",
    methods=["PUT"]
)
@login_required
def edit_object(
    object_id
):

    try:

        object_id = ObjectId(
            object_id
        )

    except Exception:

        return jsonify({
            "status": "error",
            "message": "Invalid object ID"
        }), 400


    existing_object = get_object_by_id(
        object_id
    )


    if not existing_object:

        return jsonify({
            "status": "error",
            "message": "Object not found"
        }), 404


    if (
        str(existing_object["user_id"])
        != session["user_id"]
    ):

        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403


    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400


    allowed_fields = [
        "name",
        "category",
        "expiry_date",
        "quantity",
        "notes"
    ]


    update_data = {}


    for field in allowed_fields:

        if field in data:

            update_data[field] = data[
                field
            ]


    if not update_data:

        return jsonify({
            "status": "error",
            "message": "No valid fields to update"
        }), 400


    if "quantity" in update_data:

        try:

            quantity = int(
                update_data["quantity"]
            )

            if quantity <= 0:
                raise ValueError

            update_data["quantity"] = quantity

        except ValueError:

            return jsonify({
                "status": "error",
                "message": "Quantity must be positive"
            }), 400


    if "expiry_date" in update_data:

        try:

            datetime.strptime(
                update_data["expiry_date"],
                "%Y-%m-%d"
            )

        except ValueError:

            return jsonify({
                "status": "error",
                "message": "Invalid expiry date"
            }), 400


    update_data[
        "updated_at"
    ] = datetime.utcnow()


    # --------------------------------------------------
    # RESET REMINDER HISTORY IF EXPIRY DATE CHANGES
    # --------------------------------------------------

    if "expiry_date" in update_data:

        update_data[
            "last_reminder_level"
        ] = None

        update_data[
            "last_reminder_date"
        ] = None

        update_data[
            "last_reminder_sent_at"
        ] = None


    update_object(
        object_id,
        update_data
    )


    return jsonify({

        "status": "success",

        "message": "Object updated successfully"

    }), 200


# ==================================================
# DELETE OBJECT API
# ==================================================

@object_bp.route(
    "/<object_id>",
    methods=["DELETE"]
)
@login_required
def remove_object(
    object_id
):

    try:

        object_id = ObjectId(
            object_id
        )

    except Exception:

        return jsonify({
            "status": "error",
            "message": "Invalid object ID"
        }), 400


    existing_object = get_object_by_id(
        object_id
    )


    if not existing_object:

        return jsonify({
            "status": "error",
            "message": "Object not found"
        }), 404


    if (
        str(existing_object["user_id"])
        != session["user_id"]
    ):

        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403


    image_filename = existing_object.get(
        "image"
    )


    if image_filename:

        upload_folder = os.path.join(
            current_app.root_path,
            current_app.config[
                "UPLOAD_FOLDER"
            ]
        )


        image_path = os.path.join(
            upload_folder,
            image_filename
        )


        if os.path.exists(
            image_path
        ):

            os.remove(
                image_path
            )


    delete_object(
        object_id
    )


    return jsonify({

        "status": "success",

        "message": "Object deleted successfully"

    }), 200