from functools import wraps

from flask import session, redirect, url_for


def login_required(function):
    """
    Allow access only to logged-in users.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("auth.login")
            )

        return function(*args, **kwargs)

    return decorated_function