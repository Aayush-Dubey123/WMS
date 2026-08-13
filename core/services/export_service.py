"""
export_service.py — File export service generating CSV and Excel (.xlsx) files.

Converts filtered data feeds into downloadable file streams using openpyxl and csv module.
"""

import csv
import io
from typing import Any

import openpyxl

from core import logger

logging = logger(__name__)


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
    """
    Retrieve global ExportService instance.

    Returns:
        ExportService: Shared export service instance.
    """
    global _export_service_instance
    if _export_service_instance is None:
        _export_service_instance = ExportService()
    return _export_service_instance
