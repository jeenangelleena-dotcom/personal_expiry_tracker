import os
import re
import logging
from urllib.parse import urlsplit, urlunsplit
from flask_pymongo import PyMongo
from config import Config

logger = logging.getLogger(__name__)

# Create Flask-PyMongo object
mongo = PyMongo()


def sanitize_mongo_uri(uri: str) -> str:
    """
    Mask credentials in a MongoDB connection string for safe logging.
    """
    if not uri:
        return ""
    return re.sub(r":([^/@]+)@", r":****@", uri)


def build_mongo_uri(raw_uri: str, db_name: str) -> str:
    """
    Construct a valid MongoDB URI by placing the database name before
    any query parameters, avoiding malformed URIs on MongoDB Atlas.
    """
    if not raw_uri:
        return raw_uri

    uri = raw_uri.strip()
    parsed = urlsplit(uri)
    existing_path = parsed.path.strip("/")

    # If the URI already has a database name in the path, use it
    if existing_path:
        return uri

    # If a database name is provided separately, insert it into the path
    target_db = (db_name or "").strip()
    if target_db:
        new_path = f"/{target_db}"
        return urlunsplit((
            parsed.scheme,
            parsed.netloc,
            new_path,
            parsed.query,
            parsed.fragment
        ))

    return uri


def init_mongodb(app):
    """
    Initialize MongoDB with the Flask application.
    Reuses the client connection pool across serverless invocations.
    """
    raw_uri = Config.MONGO_URI or os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    db_name = Config.MONGO_DB_NAME or os.getenv("MONGO_DB_NAME", "personal_expiry_tracker")

    final_uri = build_mongo_uri(raw_uri, db_name)
    app.config["MONGO_URI"] = final_uri

    safe_uri = sanitize_mongo_uri(final_uri)
    logger.info("Initializing MongoDB with URI: %s", safe_uri)

    try:
        mongo.init_app(app)
    except Exception as error:
        logger.error("Failed to initialize Flask-PyMongo: %s", error)
        raise

    return mongo


def get_database():
    """
    Return the MongoDB database object.
    Safely resolves the database whether configured via URI path or MONGO_DB_NAME.
    """
    if mongo.db is not None:
        return mongo.db

    if mongo.cx is not None:
        db_name = Config.MONGO_DB_NAME or os.getenv("MONGO_DB_NAME", "personal_expiry_tracker")
        return mongo.cx[db_name]

    raise RuntimeError("MongoDB has not been initialized.")


def get_users_collection():
    """
    Return the users collection.
    """
    return get_database().users


def get_objects_collection():
    """
    Return the objects collection.
    """
    return get_database().objects


def create_indexes():
    """
    Create MongoDB indexes used by the application.
    Safely wrapped to avoid breaking serverless function cold starts.
    """
    try:
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
    except Exception as error:
        logger.warning("Could not ensure MongoDB indexes: %s", error)