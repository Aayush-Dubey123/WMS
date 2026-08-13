"""
user_crud.py — Persistence layer for user document operations in MongoDB.

Provides methods for user creation, lookup by email/ID/warehouse, update, and deletion.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_user_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB document dictionary into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document dictionary.

    Returns:
        Dict[str, Any]: Formatted user dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDUser:
    """Database persistence access layer for User documents."""

    async def create(self, user_in: dict) -> dict:
        """
        Create a new user document in users collection.

        Args:
            user_in (dict): User document payload dictionary.

        Returns:
            dict: Inserted user document payload.

        Raises:
            Exception: If database insertion fails.
        """
        try:
            logging.info("Executing CRUDUser.create")
            db = MongoDatabase()
            user_data = dict(user_in)
            result = await db.users.insert_one(user_data)
            user_data["_id"] = result.inserted_id
            return _format_user_doc(user_data)
        except Exception as error:
            logging.error(f"Error in CRUDUser.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """
        Retrieve user document by unique string ID.

        Args:
            id (str): User ID string (ObjectId hex string).

        Returns:
            Optional[dict]: User dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDUser.get_by_id for ID: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.users.find_one({"_id": query_id})
            return _format_user_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDUser.get_by_id: {error}")
            raise

    async def get_by_email(self, email: str) -> dict | None:
        """
        Retrieve user document by unique email address.

        Args:
            email (str): User email address.

        Returns:
            Optional[dict]: User dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDUser.get_by_email for: {email}")
            db = MongoDatabase()
            doc = await db.users.find_one({"email": email.lower().strip()})
            return _format_user_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDUser.get_by_email: {error}")
            raise

    async def get_by_warehouse(self, warehouse_id: str, role: str | None = None) -> list[dict]:
        """
        Retrieve list of users assigned to a warehouse, optionally filtered by role.

        Args:
            warehouse_id (str): Target warehouse ID.
            role (Optional[str]): Optional role filter string.

        Returns:
            List[dict]: List of matching user dictionary records.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDUser.get_by_warehouse for WH: {warehouse_id}")
            db = MongoDatabase()
            filter_query: dict[str, Any] = {"warehouse_id": warehouse_id}
            if role:
                filter_query["role"] = role
            cursor = db.users.find(filter_query)
            docs = await cursor.to_list(length=1000)
            return [_format_user_doc(doc) for doc in docs]
        except Exception as error:
            logging.error(f"Error in CRUDUser.get_by_warehouse: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """
        Update user document fields by unique ID.

        Args:
            id (str): User ID string.
            update_in (dict): Dictionary of fields to update.

        Returns:
            Optional[dict]: Updated user record dictionary if found, None otherwise.

        Raises:
            Exception: If update operation fails.
        """
        try:
            logging.info(f"Executing CRUDUser.update for ID: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.users.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_user_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDUser.update: {error}")
            raise

    async def list_users(self, filter_query: dict | None = None, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """
        List users with filtering and pagination.

        Args:
            filter_query (Optional[dict]): MongoDB filter query object.
            skip (int): Records to skip for pagination.
            limit (int): Maximum records to return.

        Returns:
            tuple[List[dict], int]: List of user dictionaries and total matching count.

        Raises:
            Exception: If list query fails.
        """
        try:
            logging.info("Executing CRUDUser.list_users")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.users.count_documents(query)
            cursor = db.users.find(query).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_user_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDUser.list_users: {error}")
            raise
