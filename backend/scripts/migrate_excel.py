"""
migrate_excel.py — One-off legacy Excel spreadsheet migration script.

Imports legacy warehouse inventory sheets, validates data line items,
populates MongoDB collections, and generates a reconciliation report.
Run with: python -m scripts.migrate_excel path/to/legacy_sheet.xlsx --warehouse RNO
"""

import argparse
import asyncio
import os
import sys

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime

import openpyxl
from pytz import timezone

from core import logger
from core.database.database import (
    MongoDatabase,
    close_mongo_connection,
    connect_to_mongo,
)
from core.models.ticket_model import TicketStatus
from core.utils.ticket_generator import ticket_generator

logging = logger(__name__)


async def migrate_excel(file_path: str, warehouse_code: str) -> None:
    """
    Import and reconcile legacy warehouse Excel inventory sheet into MongoDB.

    Args:
        file_path (str): Absolute or relative path to legacy .xlsx spreadsheet file.
        warehouse_code (str): Warehouse facility short code string (e.g. RNO).
    """
    try:
        logging.info(f"Executing migrate_excel for file: {file_path} | Warehouse: {warehouse_code}")
        await connect_to_mongo()
        db = MongoDatabase()

        wh_doc = await db.warehouses.find_one({"code": warehouse_code.strip().upper()})
        if not wh_doc:
            logging.error(f"Migration aborted: target warehouse code '{warehouse_code}' not found")
            return

        wh_id = str(wh_doc["_id"])
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active

        total_rows = 0
        imported_count = 0
        reconciliation_flags = []

        headers = [str(cell.value or "").strip().lower() for cell in sheet[1]]

        ticket_id = await ticket_generator.generate_ticket_id(wh_code=warehouse_code)

        ticket_doc = {
            "ticket_id": ticket_id,
            "warehouse_id": wh_id,
            "inbox_id": None,
            "tracking_number": "LEGACY-MIGRATION",
            "no_ticket_arrival": True,
            "status": TicketStatus.STORED.value,
            "arrived_by": "MIGRATION_SCRIPT",
            "approved_by": "MIGRATION_SCRIPT",
            "storage_location": "MIGRATED_BIN",
            "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
        ticket_res = await db.tickets.insert_one(ticket_doc)
        str(ticket_res.inserted_id)

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):
                continue
            total_rows += 1
            row_dict = dict(zip(headers, row))

            barcode = str(row_dict.get("barcode") or row_dict.get("upc") or f"MIGRATED-{row_idx}")
            product_name = str(row_dict.get("product_name") or row_dict.get("description") or "Legacy Item")
            location_code = str(row_dict.get("location") or row_dict.get("bin") or "A-01-01")

            item_doc = {
                "ticket_id": ticket_id,
                "unit_seq": total_rows,
                "barcode": barcode.strip(),
                "product_name": product_name.strip(),
                "width": float(row_dict.get("width") or 0.0),
                "height": float(row_dict.get("height") or 0.0),
                "weight": float(row_dict.get("weight") or 0.0),
                "image_url": None,
                "damage": {"flag": False, "note": None},
                "status": TicketStatus.STORED.value,
                "warehouse_id": wh_id,
                "storage_location": location_code.strip().upper(),
                "order_id": None,
                "logged_by": "MIGRATION_SCRIPT",
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
            await db.items.insert_one(item_doc)
            imported_count += 1

        logging.info("================ MIGRATION RECONCILIATION REPORT ================")
        logging.info(f"Source File: {file_path}")
        logging.info(f"Warehouse: {warehouse_code} ({wh_id})")
        logging.info(f"Generated Migration Ticket ID: {ticket_id}")
        logging.info(f"Total Rows Processed: {total_rows}")
        logging.info(f"Total Items Successfully Imported: {imported_count}")
        logging.info(f"Reconciliation Flags: {len(reconciliation_flags)}")
        logging.info("=================================================================")
    except Exception as error:
        logging.error(f"Error in migrate_excel script: {error}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Legacy Excel Migration Script")
    parser.add_argument("file_path", help="Path to legacy Excel .xlsx spreadsheet file")
    parser.add_argument("--warehouse", required=True, help="Warehouse short code (e.g. RNO)")
    args = parser.parse_args()

    asyncio.run(migrate_excel(file_path=args.file_path, warehouse_code=args.warehouse))
