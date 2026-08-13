"""
api_key_crud.py — Persistence layer for api_keys collection in MongoDB.

Provides methods for creating, validating key hashes, listing, and revoking API keys.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_key_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB API key document into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document.

    Returns:
        Dict[str, Any]: Formatted API key dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDApiKey:
    """Database persistence access layer for ApiKey documents."""

    async def create(self, key_in: dict) -> dict:
        """
        Create a new API key document.

        Args:
            key_in (dict): API key payload.

        Returns:
            dict: Inserted API key document.

        Raises:
            Exception: If insertion fails.
        """
        try:
            logging.info("Executing CRUDApiKey.create")
            db = MongoDatabase()
            data = dict(key_in)
            result = await db.api_keys.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_key_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDApiKey.create: {error}")
            raise

    async def get_by_hash(self, key_hash: str) -> dict | None:
        """
        Retrieve active API key document by key hash string.

        Args:
            key_hash (str): Hash string of raw API key.

        Returns:
            Optional[dict]: ApiKey dictionary if found and active, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info("Executing CRUDApiKey.get_by_hash")
            db = MongoDatabase()
            doc = await db.api_keys.find_one({"key_hash": key_hash, "is_active": True})
            return _format_key_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDApiKey.get_by_hash: {error}")
            raise

    async def list_keys(self, user_id: str) -> list[dict]:
        """
        List all API keys created by user.

        Args:
            user_id (str): User ID string.

        Returns:
            List[dict]: List of API key documents.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDApiKey.list_keys for user: {user_id}")
            db = MongoDatabase()
            cursor = db.api_keys.find({"created_by": user_id})
            docs = await cursor.to_list(length=100)
            return [_format_key_doc(doc) for doc in docs]
        except Exception as error:
            logging.error(f"Error in CRUDApiKey.list_keys: {error}")
            raise

    async def revoke(self, id: str) -> dict | None:
        """
        Revoke an API key (sets is_active=False).

        Args:
            id (str): API key ID.

        Returns:
            Optional[dict]: Updated API key record.

        Raises:
            Exception: If update fails.
        """
        try:
            logging.info(f"Executing CRUDApiKey.revoke: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.api_keys.find_one_and_update(
                {"_id": query_id},
                {"$set": {"is_active": False}},
                return_document=True,
            )
            return _format_key_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDApiKey.revoke: {error}")
            raise
