from datetime import datetime

from bson import ObjectId

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models.user_model import (
    create_user,
    find_user_by_email
)

from database.mongodb import (
    get_users_collection
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name:
            flash(
                "Name is required.",
                "error"
            )
            return render_template(
                "register.html"
            )

        if not email:
            flash(
                "Email is required.",
                "error"
            )
            return render_template(
                "register.html"
            )

        if not password:
            flash(
                "Password is required.",
                "error"
            )
            return render_template(
                "register.html"
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "error"
            )
            return render_template(
                "register.html"
            )
        existing_user = find_user_by_email(
            email
        )

        if existing_user:

            flash(
                "Email is already registered. Please login.",
                "error"
            )

            return render_template(
                "register.html"
            )

        user_data = {
            "name": name,
            "email": email,
            "password": generate_password_hash(
                password
            ),
            "created_at": datetime.utcnow()
        }

        create_user(user_data)

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Email and password are required.",
                "error"
            )

            return render_template(
                "login.html"
            )

        user = find_user_by_email(
            email
        )

        if not user:

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html"
            )
        stored_password = user.get(
            "password"
        )

        if not stored_password:

            flash(
                "This account does not have a valid password. Please register again.",
                "error"
            )

            return render_template(
                "login.html"
            )

        password_valid = check_password_hash(
            stored_password,
            password
        )

        if not password_valid:

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html"
            )
        session.clear()

        session["user_id"] = str(
            user["_id"]
        )

        session["user_name"] = user.get(
            "name",
            "User"
        )

        session["user_email"] = user.get(
            "email",
            ""
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )

@auth_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("home")
    )

@auth_bp.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("auth.login")
        )

    try:

        user_id = ObjectId(
            session["user_id"]
        )

    except Exception:

        session.clear()

        return redirect(
            url_for("auth.login")
        )

    user = get_users_collection().find_one(
        {
            "_id": user_id
        }
    )

    if not user:

        session.clear()

        flash(
            "User account not found.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "profile.html",
        user=user
    )