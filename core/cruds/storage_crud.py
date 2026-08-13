"""
storage_crud.py — Persistence layer for storage_locations collection in MongoDB.

Provides queries for creating, looking up, and updating physical storage locations.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_storage_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB storage location document into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document.

    Returns:
        Dict[str, Any]: Formatted storage location dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDStorageLocation:
    """Database persistence access layer for StorageLocation documents."""

    async def create(self, storage_in: dict) -> dict:
        """
        Create a new storage location document.

        Args:
            storage_in (dict): Storage location payload.

        Returns:
            dict: Inserted storage location record.

        Raises:
            Exception: If insertion fails.
        """
        try:
            logging.info("Executing CRUDStorageLocation.create")
            db = MongoDatabase()
            data = dict(storage_in)
            result = await db.storage_locations.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_storage_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDStorageLocation.create: {error}")
            raise

    async def get_by_code(self, warehouse_id: str, location_code: str) -> dict | None:
        """
        Retrieve storage location document by warehouse ID and location code.

        Args:
            warehouse_id (str): Target warehouse ID.
            location_code (str): Location code string (e.g. A-04-12).

        Returns:
            Optional[dict]: Storage location dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDStorageLocation.get_by_code: {location_code} in WH {warehouse_id}")
            db = MongoDatabase()
            doc = await db.storage_locations.find_one(
                {"warehouse_id": warehouse_id, "location_code": location_code.strip().upper()}
            )
            return _format_storage_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDStorageLocation.get_by_code: {error}")
            raise

    async def list_locations(self, warehouse_id: str, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """
        List storage locations for a warehouse.

        Args:
            warehouse_id (str): Target warehouse facility ID.
            skip (int): Offset count.
            limit (int): Maximum items to return.

        Returns:
            tuple[List[dict], int]: List of storage location dictionaries and total count.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDStorageLocation.list_locations for WH: {warehouse_id}")
            db = MongoDatabase()
            query = {"warehouse_id": warehouse_id}
            total = await db.storage_locations.count_documents(query)
            cursor = db.storage_locations.find(query).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_storage_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDStorageLocation.list_locations: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """
        Update storage location document by ID.

        Args:
            id (str): Storage location ID.
            update_in (dict): Fields to update.

        Returns:
            Optional[dict]: Updated storage location record.

        Raises:
            Exception: If update fails.
        """
        try:
            logging.info(f"Executing CRUDStorageLocation.update: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.storage_locations.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_storage_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDStorageLocation.update: {error}")
            raise
