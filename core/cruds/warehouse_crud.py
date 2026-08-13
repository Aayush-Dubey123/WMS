"""
warehouse_crud.py — Persistence layer for warehouse document operations in MongoDB.

Provides methods for warehouse creation, retrieval by code/ID, update, and listing.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_wh_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB document dictionary into standard warehouse schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document dictionary.

    Returns:
        Dict[str, Any]: Formatted warehouse dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDWarehouse:
    """Database persistence access layer for Warehouse documents."""

    async def create(self, wh_in: dict) -> dict:
        """
        Create a new warehouse document in warehouses collection.

        Args:
            wh_in (dict): Warehouse document payload dictionary.

        Returns:
            dict: Inserted warehouse document payload.

        Raises:
            Exception: If database insertion fails.
        """
        try:
            logging.info("Executing CRUDWarehouse.create")
            db = MongoDatabase()
            wh_data = dict(wh_in)
            result = await db.warehouses.insert_one(wh_data)
            wh_data["_id"] = result.inserted_id
            return _format_wh_doc(wh_data)
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """
        Retrieve warehouse document by unique string ID.

        Args:
            id (str): Warehouse ID string.

        Returns:
            Optional[dict]: Warehouse dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDWarehouse.get_by_id for ID: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.warehouses.find_one({"_id": query_id})
            return _format_wh_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.get_by_id: {error}")
            raise

    async def get_by_code(self, code: str) -> dict | None:
        """
        Retrieve warehouse document by unique warehouse short code.

        Args:
            code (str): Warehouse short code identifier (e.g., RNO).

        Returns:
            Optional[dict]: Warehouse dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDWarehouse.get_by_code for code: {code}")
            db = MongoDatabase()
            doc = await db.warehouses.find_one({"code": code.strip().upper()})
            return _format_wh_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.get_by_code: {error}")
            raise

    async def list_warehouses(self, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """
        List all warehouse facilities with pagination.

        Args:
            skip (int): Records to skip for pagination.
            limit (int): Maximum records to return.

        Returns:
            tuple[List[dict], int]: List of warehouse dictionaries and total record count.

        Raises:
            Exception: If listing query fails.
        """
        try:
            logging.info("Executing CRUDWarehouse.list_warehouses")
            db = MongoDatabase()
            total = await db.warehouses.count_documents({})
            cursor = db.warehouses.find({}).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_wh_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.list_warehouses: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """
        Update warehouse document fields by unique ID.

        Args:
            id (str): Warehouse ID string.
            update_in (dict): Dictionary of fields to update.

        Returns:
            Optional[dict]: Updated warehouse record dictionary if found, None otherwise.

        Raises:
            Exception: If update operation fails.
        """
        try:
            logging.info(f"Executing CRUDWarehouse.update for ID: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.warehouses.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_wh_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.update: {error}")
            raise
