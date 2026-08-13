"""
integration_service.py — Consolidated integration services for storage and export operations.

Merges integration-related service facades:
- LocalStorageService: Local volume file storage for item photo uploads
- ExportService: File export service generating CSV and Excel files
"""

import csv
import io
import os
import uuid
from typing import Any

import aiofiles
import openpyxl
from fastapi import HTTPException, UploadFile, status

from core import logger

logging = logger(__name__)


# ====== LOCAL STORAGE SERVICE ======

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
    """Retrieve global LocalStorageService instance."""
    global _storage_service_instance
    if _storage_service_instance is None:
        _storage_service_instance = LocalStorageService()
    return _storage_service_instance


# ====== EXPORT SERVICE ======

class ExportService:
    """Service facade generating downloadable report files."""

    def generate_csv(self, records: list[dict[str, Any]]) -> bytes:
        """
        Convert list of dictionary records into CSV byte stream.

        Args:
            records (List[Dict[str, Any]]): List of row dictionaries.

        Returns:
            bytes: UTF-8 encoded CSV file bytes.
        """
        logging.info("Executing ExportService.generate_csv")
        if not records:
            return b""

        output = io.StringIO()
        fieldnames = list(records[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow(row)

        return output.getvalue().encode("utf-8")

    def generate_xlsx(self, records: list[dict[str, Any]], title: str = "Report") -> bytes:
        """
        Convert list of dictionary records into Excel (.xlsx) file byte stream using openpyxl.

        Args:
            records (List[Dict[str, Any]]): List of row dictionaries.
            title (str): Worksheet title header.

        Returns:
            bytes: OpenPyXL generated XLSX file bytes.
        """
        logging.info("Executing ExportService.generate_xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title[:30]

        if not records:
            ws.append(["No records found"])
            stream = io.BytesIO()
            wb.save(stream)
            return stream.getvalue()

        headers = list(records[0].keys())
        ws.append(headers)

        for row in records:
            ws.append([str(row.get(h, "")) if isinstance(row.get(h), (dict, list)) else row.get(h, "") for h in headers])

        stream = io.BytesIO()
        wb.save(stream)
        return stream.getvalue()


_export_service_instance: ExportService | None = None


def get_export_service() -> ExportService:
    """Retrieve global ExportService instance."""
    global _export_service_instance
    if _export_service_instance is None:
        _export_service_instance = ExportService()
    return _export_service_instance
