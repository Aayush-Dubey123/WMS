"""
order_crud.py — Persistence layer for orders collection in MongoDB.

Provides CRUD methods for customer order document queries and status updates.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_order_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB order document into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document.

    Returns:
        Dict[str, Any]: Formatted order dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDOrder:
    """Database persistence access layer for Order documents."""

    async def create(self, order_in: dict) -> dict:
        """
        Create a new order document.

        Args:
            order_in (dict): Order payload dictionary.

        Returns:
            dict: Inserted order document.

        Raises:
            Exception: If insertion fails.
        """
        try:
            logging.info("Executing CRUDOrder.create")
            db = MongoDatabase()
            data = dict(order_in)
            result = await db.orders.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_order_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDOrder.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """
        Retrieve order document by unique string ID or order_id string.

        Args:
            id (str): Order MongoDB ObjectId string or order_id code.

        Returns:
            Optional[dict]: Order dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDOrder.get_by_id: {id}")
            db = MongoDatabase()
            filter_doc = {"_id": ObjectId(id)} if ObjectId.is_valid(id) else {"order_id": id}
            doc = await db.orders.find_one(filter_doc)
            return _format_order_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDOrder.get_by_id: {error}")
            raise

    async def get_by_order_id(self, order_id: str) -> dict | None:
        """
        Retrieve order document by unique order_id code (e.g. ORD-1001).

        Args:
            order_id (str): Order ID code string.

        Returns:
            Optional[dict]: Order dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDOrder.get_by_order_id: {order_id}")
            db = MongoDatabase()
            doc = await db.orders.find_one({"order_id": order_id.strip()})
            return _format_order_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDOrder.get_by_order_id: {error}")
            raise

    async def list_orders(self, filter_query: dict | None = None, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """
        List orders with filtering and pagination.

        Args:
            filter_query (Optional[dict]): Filter query object.
            skip (int): Offset count.
            limit (int): Maximum records.

        Returns:
            tuple[List[dict], int]: List of order dictionaries and total count.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info("Executing CRUDOrder.list_orders")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.orders.count_documents(query)
            cursor = db.orders.find(query).sort("created_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_order_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDOrder.list_orders: {error}")
            raise

    async def update(self, id: str, update_in: dict, session=None) -> dict | None:
        """
        Update order fields by unique ID or order_id string, optionally within a session transaction.

        Args:
            id (str): Order ID string.
            update_in (dict): Fields to update.
            session: Optional Motor client session for MongoDB transaction.

        Returns:
            Optional[dict]: Updated order dictionary.

        Raises:
            Exception: If update fails.
        """
        try:
            logging.info(f"Executing CRUDOrder.update: {id}")
            db = MongoDatabase()
            filter_doc = {"_id": ObjectId(id)} if ObjectId.is_valid(id) else {"order_id": id}
            result = await db.orders.find_one_and_update(
                filter_doc,
                {"$set": update_in},
                return_document=True,
                session=session,
            )
            return _format_order_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDOrder.update: {error}")
            raise
