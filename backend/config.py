import os

from dotenv import load_dotenv


# Load values from .env file
load_dotenv()


class Config:

    # Flask secret key
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "personal-expiry-tracker-secret-key"
    )

    # MongoDB connection
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://127.0.0.1:27017/"
    )

    # MongoDB database name
    MONGO_DB_NAME = os.getenv(
        "MONGO_DB_NAME",
        "personal_expiry_tracker"
    )

    # Uploaded image location
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        "uploads"
    )

    # Maximum uploaded file size: 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Allowed image extensions
    ALLOWED_IMAGE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    # Email configuration
    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        ""
    )

    MAIL_PORT = int(
        os.getenv(
            "MAIL_PORT",
            "587"
        )
    )

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
        ""
    )

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD",
        ""
    )

    MAIL_USE_TLS = True