"""
item_crud.py — Persistence layer for items collection in MongoDB.

Provides methods for creating scanned items, bulk unit count queries, and status updates.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_item_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB item document into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document.

    Returns:
        Dict[str, Any]: Formatted item dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDItem:
    """Database persistence access layer for Item documents."""

    async def create(self, item_in: dict) -> dict:
        """
        Create a new item document.

        Args:
            item_in (dict): Item creation payload.

        Returns:
            dict: Inserted item document payload.

        Raises:
            Exception: If insertion fails.
        """
        try:
            logging.info("Executing CRUDItem.create")
            db = MongoDatabase()
            data = dict(item_in)
            result = await db.items.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_item_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDItem.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """
        Retrieve item by unique string ID.

        Args:
            id (str): Item ID.

        Returns:
            Optional[dict]: Item dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDItem.get_by_id: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.items.find_one({"_id": query_id})
            return _format_item_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDItem.get_by_id: {error}")
            raise

    async def get_next_unit_seq(self, ticket_id: str) -> int:
        """
        Calculate next sequential unit index (1..N) for a given ticket.

        Args:
            ticket_id (str): Generated ticket ID string.

        Returns:
            int: Next unit sequence integer.

        Raises:
            Exception: If count query fails.
        """
        try:
            logging.info(f"Executing CRUDItem.get_next_unit_seq for ticket: {ticket_id}")
            db = MongoDatabase()
            count = await db.items.count_documents({"ticket_id": ticket_id})
            return count + 1
        except Exception as error:
            logging.error(f"Error in CRUDItem.get_next_unit_seq: {error}")
            raise

    async def get_items_by_ticket(self, ticket_id: str) -> list[dict]:
        """
        Retrieve all items registered under a ticket_id.

        Args:
            ticket_id (str): Generated ticket ID string.

        Returns:
            List[dict]: List of item dictionaries.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDItem.get_items_by_ticket: {ticket_id}")
            db = MongoDatabase()
            cursor = db.items.find({"ticket_id": ticket_id}).sort("unit_seq", 1)
            docs = await cursor.to_list(length=1000)
            return [_format_item_doc(doc) for doc in docs]
        except Exception as error:
            logging.error(f"Error in CRUDItem.get_items_by_ticket: {error}")
            raise

    async def update_status_by_ticket(self, ticket_id: str, status_value: str) -> int:
        """
        Update status for all items attached to a ticket_id (except damaged items).

        Args:
            ticket_id (str): Ticket ID string.
            status_value (str): Target status string.

        Returns:
            int: Number of updated item documents.

        Raises:
            Exception: If bulk update fails.
        """
        try:
            logging.info(f"Executing CRUDItem.update_status_by_ticket: {ticket_id} -> {status_value}")
            db = MongoDatabase()
            result = await db.items.update_many(
                {"ticket_id": ticket_id, "damage.flag": False},
                {"$set": {"status": status_value}},
            )
            return result.modified_count
        except Exception as error:
            logging.error(f"Error in CRUDItem.update_status_by_ticket: {error}")
            raise

    async def update_item(self, id: str, update_in: dict) -> dict | None:
        """
        Update single item document fields by ID.

        Args:
            id (str): Item ID string.
            update_in (dict): Fields to update.

        Returns:
            Optional[dict]: Updated item dictionary if found.

        Raises:
            Exception: If update fails.
        """
        try:
            logging.info(f"Executing CRUDItem.update_item: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.items.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_item_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDItem.update_item: {error}")
            raise
