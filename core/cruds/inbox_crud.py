"""
inbox_crud.py — Persistence layer for inbox_shipments collection in MongoDB.

Provides queries for seller shipment announcements, acceptance, rejection, and comments.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_inbox_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB document dictionary into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document.

    Returns:
        Dict[str, Any]: Formatted inbox dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDInbox:
    """Database persistence access layer for InboxShipment documents."""

    async def create(self, inbox_in: dict) -> dict:
        """
        Create a new inbox shipment record.

        Args:
            inbox_in (dict): Inbox document dictionary.

        Returns:
            dict: Inserted inbox record.

        Raises:
            Exception: If insertion fails.
        """
        try:
            logging.info("Executing CRUDInbox.create")
            db = MongoDatabase()
            data = dict(inbox_in)
            result = await db.inbox_shipments.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_inbox_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDInbox.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """
        Retrieve inbox shipment by unique ID string.

        Args:
            id (str): Inbox shipment ID.

        Returns:
            Optional[dict]: Inbox dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDInbox.get_by_id: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.inbox_shipments.find_one({"_id": query_id})
            return _format_inbox_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDInbox.get_by_id: {error}")
            raise

    async def get_by_tracking(self, tracking_number: str) -> dict | None:
        """
        Retrieve accepted inbox shipment by tracking number string.

        Args:
            tracking_number (str): Carrier tracking number.

        Returns:
            Optional[dict]: Inbox dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDInbox.get_by_tracking: {tracking_number}")
            db = MongoDatabase()
            doc = await db.inbox_shipments.find_one({"tracking_number": tracking_number.strip()})
            return _format_inbox_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDInbox.get_by_tracking: {error}")
            raise

    async def list_shipments(self, filter_query: dict | None = None, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """
        List inbox shipments with filtering and pagination.

        Args:
            filter_query (Optional[dict]): Filter query dictionary.
            skip (int): Records to skip.
            limit (int): Maximum records.

        Returns:
            tuple[List[dict], int]: List of inbox dictionaries and total count.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info("Executing CRUDInbox.list_shipments")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.inbox_shipments.count_documents(query)
            cursor = db.inbox_shipments.find(query).sort("created_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_inbox_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDInbox.list_shipments: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """
        Update inbox shipment fields by unique ID.

        Args:
            id (str): Inbox ID string.
            update_in (dict): Fields to update.

        Returns:
            Optional[dict]: Updated inbox dictionary if found, None otherwise.

        Raises:
            Exception: If update fails.
        """
        try:
            logging.info(f"Executing CRUDInbox.update: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.inbox_shipments.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_inbox_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDInbox.update: {error}")
            raise

    async def add_comment(self, id: str, comment_doc: dict) -> dict | None:
        """
        Push a comment document into inbox shipment comments thread.

        Args:
            id (str): Inbox ID string.
            comment_doc (dict): Comment payload dictionary.

        Returns:
            Optional[dict]: Updated inbox document.

        Raises:
            Exception: If push operation fails.
        """
        try:
            logging.info(f"Executing CRUDInbox.add_comment: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.inbox_shipments.find_one_and_update(
                {"_id": query_id},
                {"$push": {"comments": comment_doc}},
                return_document=True,
            )
            return _format_inbox_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDInbox.add_comment: {error}")
            raise
