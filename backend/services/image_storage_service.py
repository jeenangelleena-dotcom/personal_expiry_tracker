import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import current_app

logger = logging.getLogger(__name__)


def is_cloudinary_configured() -> bool:
    """
    Check if Cloudinary environment variables are configured.
    """
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    cloudinary_url = os.getenv("CLOUDINARY_URL")

    return bool((cloud_name and api_key and api_secret) or cloudinary_url)


def save_image(image_file) -> str:
    """
    Save an uploaded image file.
    If Cloudinary is configured (recommended for Vercel production),
    uploads to Cloudinary and returns the secure URL.
    Otherwise, saves to the local upload directory and returns the filename.
    """
    if not image_file or not image_file.filename:
        return None

    filename = secure_filename(image_file.filename)
    if not filename:
        filename = f"image_{uuid.uuid4().hex[:8]}.jpg"

    # Attempt Cloudinary upload if configured
    if is_cloudinary_configured():
        try:
            import cloudinary
            import cloudinary.uploader

            cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
            api_key = os.getenv("CLOUDINARY_API_KEY")
            api_secret = os.getenv("CLOUDINARY_API_SECRET")
            cloudinary_url = os.getenv("CLOUDINARY_URL")

            if cloudinary_url:
                cloudinary.config(cloudinary_url=cloudinary_url)
            else:
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    secure=True
                )

            image_file.seek(0)
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="personal_expiry_tracker",
                resource_type="image"
            )
            secure_url = upload_result.get("secure_url")
            logger.info("Successfully uploaded image to Cloudinary: %s", secure_url)
            return secure_url

        except Exception as error:
            logger.error("Cloudinary upload failed: %s", error)
            # On Vercel, if Cloudinary was configured but failed, raise clear error
            if os.getenv("VERCEL") == "1":
                raise RuntimeError(
                    f"Cloudinary image upload failed: {error}. "
                    "Please verify your Cloudinary credentials."
                )

    # Local filesystem storage (for development fallback)
    upload_folder = os.path.join(
        current_app.root_path,
        current_app.config.get("UPLOAD_FOLDER", "uploads")
    )

    # On Vercel serverless without Cloudinary, use /tmp to avoid read-only filesystem crash
    if os.getenv("VERCEL") == "1":
        logger.warning(
            "Cloudinary is not configured on Vercel. Storing in ephemeral /tmp/uploads. "
            "Please configure CLOUDINARY credentials for persistent storage."
        )
        upload_folder = "/tmp/uploads"

    os.makedirs(upload_folder, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    file_path = os.path.join(upload_folder, unique_filename)

    image_file.seek(0)
    image_file.save(file_path)

    return unique_filename


def delete_image(image_identifier: str) -> bool:
    """
    Delete a stored image.
    Supports both Cloudinary URLs and local filenames.
    """
    if not image_identifier:
        return False

    # Check if this is a remote URL (Cloudinary)
    if image_identifier.startswith("http://") or image_identifier.startswith("https://"):
        if is_cloudinary_configured() and "cloudinary.com" in image_identifier:
            try:
                import cloudinary
                import cloudinary.uploader

                cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
                api_key = os.getenv("CLOUDINARY_API_KEY")
                api_secret = os.getenv("CLOUDINARY_API_SECRET")
                cloudinary_url = os.getenv("CLOUDINARY_URL")

                if cloudinary_url:
                    cloudinary.config(cloudinary_url=cloudinary_url)
                else:
                    cloudinary.config(
                        cloud_name=cloud_name,
                        api_key=api_key,
                        api_secret=api_secret,
                        secure=True
                    )

                # Extract public_id: e.g. .../upload/v12345/personal_expiry_tracker/image_id.jpg
                parts = image_identifier.split("/upload/")
                if len(parts) > 1:
                    path_after_upload = parts[1]
                    segments = path_after_upload.split("/", 1)
                    if len(segments) > 1 and segments[0].startswith("v") and segments[0][1:].isdigit():
                        file_with_folder = segments[1]
                    else:
                        file_with_folder = path_after_upload

                    public_id = os.path.splitext(file_with_folder)[0]
                    cloudinary.uploader.destroy(public_id)
                    logger.info("Deleted Cloudinary image with public_id: %s", public_id)
                    return True

            except Exception as error:
                logger.error("Failed to delete Cloudinary image: %s", error)
                return False

        return True

    # Local file deletion
    try:
        upload_folder = os.path.join(
            current_app.root_path,
            current_app.config.get("UPLOAD_FOLDER", "uploads")
        )
        file_path = os.path.join(upload_folder, image_identifier)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True

        tmp_path = os.path.join("/tmp/uploads", image_identifier)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            return True

    except Exception as error:
        logger.error("Failed to delete local image: %s", error)

    return False
