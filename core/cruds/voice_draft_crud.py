"""
voice_draft_crud.py — Persistence layer for voice_drafts collection in MongoDB.

Provides methods for creating, finding, updating, and discarding VoiceDraft documents.
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_draft_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB draft document into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document.

    Returns:
        Dict[str, Any]: Formatted draft dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDVoiceDraft:
    """Database persistence access layer for VoiceDraft documents."""

    async def create(self, draft_in: dict) -> dict:
        """
        Create a new voice draft document.

        Args:
            draft_in (dict): Voice draft dictionary.

        Returns:
            dict: Inserted draft document.

        Raises:
            Exception: If insertion fails.
        """
        try:
            logging.info("Executing CRUDVoiceDraft.create")
            db = MongoDatabase()
            data = dict(draft_in)
            result = await db.voice_drafts.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_draft_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDVoiceDraft.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """
        Retrieve voice draft by unique ID string.

        Args:
            id (str): Draft ID.

        Returns:
            Optional[dict]: Draft dictionary if found, None otherwise.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info(f"Executing CRUDVoiceDraft.get_by_id: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.voice_drafts.find_one({"_id": query_id})
            return _format_draft_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDVoiceDraft.get_by_id: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """
        Update voice draft fields by unique ID.

        Args:
            id (str): Draft ID string.
            update_in (dict): Fields to update.

        Returns:
            Optional[dict]: Updated draft dictionary.

        Raises:
            Exception: If update fails.
        """
        try:
            logging.info(f"Executing CRUDVoiceDraft.update: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.voice_drafts.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_draft_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDVoiceDraft.update: {error}")
            raise
