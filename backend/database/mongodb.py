from flask_pymongo import PyMongo

from config import Config


# Create Flask-PyMongo object
mongo = PyMongo()


def init_mongodb(app):
    """
    Initialize MongoDB with the Flask application.
    """

    app.config["MONGO_URI"] = (
        Config.MONGO_URI
        + Config.MONGO_DB_NAME
    )

    mongo.init_app(app)

    return mongo


def get_database():
    """
    Return the MongoDB database object.
    """

    return mongo.db


def get_users_collection():
    """
    Return the users collection.
    """

    return mongo.db.users


def get_objects_collection():
    """
    Return the objects collection.
    """

    return mongo.db.objects


def create_indexes():
    """
    Create MongoDB indexes used by the application.
    """

    users = get_users_collection()
    objects = get_objects_collection()

    # Email must be unique
    users.create_index(
        "email",
        unique=True
    )

    # Search objects belonging to a user
    objects.create_index(
        "user_id"
    )

    # Search objects by expiry date
    objects.create_index(
        "expiry_date"
    )