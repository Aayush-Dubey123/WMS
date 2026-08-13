"""
ticket_crud.py — Persistence layer for tickets collection in MongoDB.

Provides methods for creating, finding, updating, and listing Ticket documents.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_ticket_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB ticket document into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document.

    Returns:
        Dict[str, Any]: Formatted ticket dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDTicket:
    """Database persistence access layer for Ticket documents."""

    async def create(self, ticket_in: dict) -> dict:
        """
        Create a new ticket document.

        Args:
            ticket_in (dict): Ticket creation dictionary.

        Returns:
            dict: Inserted ticket document.

        Raises:
            Exception: If insertion fails.
        """
        try:
            logging.info("Executing CRUDTicket.create")
            db = MongoDatabase()
            data = dict(ticket_in)
            result = await db.tickets.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_ticket_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDTicket.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """
        Retrieve ticket document by unique MongoDB ObjectId hex string.

        Args:
            id (str): Ticket MongoDB ID.

        Returns:
            Optional[dict]: Ticket dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDTicket.get_by_id: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.tickets.find_one({"_id": query_id})
            return _format_ticket_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDTicket.get_by_id: {error}")
            raise

    async def get_by_ticket_id(self, ticket_id: str) -> dict | None:
        """
        Retrieve ticket document by human-readable ticket_id string (e.g. RNO-20260813-001).

        Args:
            ticket_id (str): Generated ticket ID string.

        Returns:
            Optional[dict]: Ticket dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDTicket.get_by_ticket_id: {ticket_id}")
            db = MongoDatabase()
            doc = await db.tickets.find_one({"ticket_id": ticket_id.strip()})
            return _format_ticket_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDTicket.get_by_ticket_id: {error}")
            raise

    async def list_tickets(self, filter_query: dict | None = None, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """
        List tickets with filtering and pagination.

        Args:
            filter_query (Optional[dict]): Filter query dictionary.
            skip (int): Offset count.
            limit (int): Maximum records.

        Returns:
            tuple[List[dict], int]: List of tickets and total count.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info("Executing CRUDTicket.list_tickets")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.tickets.count_documents(query)
            cursor = db.tickets.find(query).sort("created_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_ticket_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDTicket.list_tickets: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """
        Update ticket fields by unique ID or ticket_id string.

        Args:
            id (str): Ticket ID or ticket_id string.
            update_in (dict): Fields dictionary to update.

        Returns:
            Optional[dict]: Updated ticket dictionary if found, None otherwise.

        Raises:
            Exception: If update fails.
        """
        try:
            logging.info(f"Executing CRUDTicket.update: {id}")
            db = MongoDatabase()
            filter_doc = {"_id": ObjectId(id)} if ObjectId.is_valid(id) else {"ticket_id": id}
            result = await db.tickets.find_one_and_update(
                filter_doc,
                {"$set": update_in},
                return_document=True,
            )
            return _format_ticket_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDTicket.update: {error}")
            raise
