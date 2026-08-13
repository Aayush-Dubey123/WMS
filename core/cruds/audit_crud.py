"""
audit_crud.py — Persistence layer for audit log operations in MongoDB.

Provides methods for writing immutable audit log records and querying audit trails.
"""

from typing import Any

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


def _format_audit_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Format raw MongoDB audit document into standard schema payload.

    Args:
        doc (Dict[str, Any]): Raw MongoDB document dictionary.

    Returns:
        Dict[str, Any]: Formatted audit dictionary.
    """
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDAuditLog:
    """Database persistence access layer for AuditLog documents."""

    async def create(self, audit_in: dict) -> dict:
        """
        Create a new audit log record in audit_log collection.

        Args:
            audit_in (dict): Audit log payload dictionary.

        Returns:
            dict: Inserted audit log document dictionary.

        Raises:
            Exception: If insertion fails.
        """
        try:
            logging.info("Executing CRUDAuditLog.create")
            db = MongoDatabase()
            audit_data = dict(audit_in)
            result = await db.audit_log.insert_one(audit_data)
            audit_data["_id"] = result.inserted_id
            return _format_audit_doc(audit_data)
        except Exception as error:
            logging.error(f"Error in CRUDAuditLog.create: {error}")
            raise

    async def list_logs(
        self, filter_query: dict | None = None, skip: int = 0, limit: int = 100
    ) -> tuple[list[dict], int]:
        """
        Query audit logs with filtering and pagination.

        Args:
            filter_query (Optional[dict]): MongoDB query filter dictionary.
            skip (int): Records to skip for pagination.
            limit (int): Maximum records to return.

        Returns:
            tuple[List[dict], int]: List of audit log dictionaries and total record count.

        Raises:
            Exception: If query fails.
        """
        try:
            logging.info("Executing CRUDAuditLog.list_logs")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.audit_log.count_documents(query)
            cursor = (
                db.audit_log.find(query)
                .sort("timestamp", -1)
                .skip(skip)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [_format_audit_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDAuditLog.list_logs: {error}")
            raise
