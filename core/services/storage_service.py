"""
storage_service.py — Local volume file storage service for item photo uploads.

Saves uploaded product inspection images locally under uploads/ directory.
"""

import os
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile, status

from core import logger

logging = logger(__name__)
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))


class LocalStorageService:
    """Service handling file save operations to local disk volume."""

    def __init__(self):
        """Initialize LocalStorageService and ensure uploads directory exists."""
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        logging.info(f"LocalStorageService initialized | Upload Dir: {UPLOAD_DIR}")

    async def save_image(self, file: UploadFile) -> str:
        """
        Save uploaded image file to local storage.

        Args:
            file (UploadFile): FastAPI UploadFile instance.

        Returns:
            str: Relative URL path string for accessing uploaded image.

        Raises:
            HTTPException 400: If file extension is not an accepted image format.
            HTTPException 500: If file writing fails.
        """
        try:
            logging.info("Executing LocalStorageService.save_image")
            extension = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
            if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
                logging.warning(f"Image upload rejected: invalid extension {extension}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image format. Allowed formats: .jpg, .jpeg, .png, .webp",
                )

            filename = f"{uuid.uuid4().hex}{extension}"
            filepath = os.path.join(UPLOAD_DIR, filename)

            async with aiofiles.open(filepath, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)

            file_url = f"/uploads/{filename}"
            logging.info(f"Image saved successfully: {file_url}")
            return file_url
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in LocalStorageService.save_image: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded image",
            )


_storage_service_instance: LocalStorageService | None = None


def get_storage_service() -> LocalStorageService:
    """
    Retrieve global LocalStorageService instance.

    Returns:
        LocalStorageService: Shared storage service instance.
    """
    global _storage_service_instance
    if _storage_service_instance is None:
        _storage_service_instance = LocalStorageService()
    return _storage_service_instance
