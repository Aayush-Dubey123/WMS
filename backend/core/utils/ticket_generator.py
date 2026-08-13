"""
ticket_generator.py — Atomic ticket sequence generator utility.

Generates structured ticket IDs in the format {WH}-{YYYYMMDD}-{SEQ:03d}.
Uses MongoDB findOneAndUpdate atomic increment on counters collection.
"""

from datetime import datetime

from pymongo import ReturnDocument
from pytz import timezone

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


class TicketGenerator:
    """
    Utility for generating unique atomic ticket IDs per warehouse and date.

    Uses MongoDB's findOneAndUpdate to increment sequence counters atomically.
    Ensures safe concurrent generation without sequence collisions.
    """

    async def generate_ticket_id(self, wh_code: str) -> str:
        """
        Generate next atomic ticket ID for a given warehouse code.

        Format: {WH}-{YYYYMMDD}-{SEQ:03d} (e.g., RNO-20260813-001).

        Args:
            wh_code (str): Warehouse code identifier (e.g., "RNO", "LAX").

        Returns:
            str: Generated atomic ticket ID string.

        Raises:
            Exception: If sequence counter increment or query fails.
        """
        try:
            logging.info(f"Executing TicketGenerator.generate_ticket_id for WH: {wh_code}")
            db = MongoDatabase()

            wh_upper = wh_code.strip().upper()
            today_str = datetime.now(timezone("UTC")).strftime("%Y%m%d")

            counter_doc = await db.counters.find_one_and_update(
                {"wh_code": wh_upper, "date_str": today_str},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            seq_number = counter_doc.get("seq", 1)
            ticket_id = f"{wh_upper}-{today_str}-{seq_number:03d}"

            logging.info(f"Generated ticket ID: {ticket_id}")
            return ticket_id
        except Exception as error:
            logging.error(f"Error in TicketGenerator.generate_ticket_id: {error}")
            raise


ticket_generator = TicketGenerator()
