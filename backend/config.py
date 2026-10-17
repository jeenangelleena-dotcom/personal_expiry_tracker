import os
import warnings
from datetime import timedelta
from dotenv import load_dotenv

# Load values from .env file if present
load_dotenv()


class Config:
    # Deployment environment detection
    IS_VERCEL = os.getenv("VERCEL") == "1"
    FLASK_ENV = os.getenv("FLASK_ENV", "production" if IS_VERCEL else "development")
    IS_PRODUCTION = IS_VERCEL or FLASK_ENV == "production"

    # Flask Secret Key
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        if IS_PRODUCTION:
            warnings.warn(
                "SECRET_KEY is not set in environment variables! "
                "Please configure SECRET_KEY in your Vercel project settings.",
                RuntimeWarning
            )
            SECRET_KEY = "personal-expiry-tracker-production-fallback-key-replace-in-env"
        else:
            SECRET_KEY = "personal-expiry-tracker-secret-key-dev"

    # Session cookie security settings (configured for HTTPS in production)
    SESSION_COOKIE_SECURE = IS_PRODUCTION
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

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

    # Uploaded image location (fallback for local development)
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

    # Cloudinary configuration (persistent image storage for Vercel)
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "")

    # Cron Job authorization secret
    CRON_SECRET = os.getenv("CRON_SECRET", "")

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