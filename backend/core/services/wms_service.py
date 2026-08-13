"""
wms_service.py — Consolidated WMS system services for audit logging and idempotency.

Merges core system service facades:
- AuditService: Service layer for system mutation audit logging
- IdempotencyService: Service enforcing idempotency key locks
"""

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from pytz import timezone

from core import logger
from core.cruds.wms_crud import CRUDAuditLog
from core.database.database import MongoDatabase

logging = logger(__name__)


# ====== AUDIT SERVICE ======

class AuditService:
    """Service facade for recording system audit trail mutations."""

    def __init__(self):
        """Initialize AuditService with CRUDAuditLog persistence handler."""
        logging.info("Executing AuditService.__init__")
        self._audit_crud = CRUDAuditLog()

    async def log_mutation(
        self,
        actor: dict[str, Any],
        action: str,
        collection: str,
        doc_id: str,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
    ) -> dict:
        """
        Record a mutation audit log entry.

        Args:
            actor (Dict[str, Any]): Authenticated user dictionary performing action.
            action (str): Mutation action identifier (e.g., CREATE, UPDATE, DELETE).
            collection (str): Target database collection name.
            doc_id (str): ID of modified document.
            before (Optional[Dict[str, Any]]): Document state prior to mutation.
            after (Optional[Dict[str, Any]]): Document state after mutation.

        Returns:
            dict: Created audit log record dictionary.

        Raises:
            Exception: If writing audit log entry fails.
        """
        try:
            logging.info(
                f"Executing AuditService.log_mutation | Action: {action} | Collection: {collection}"
            )
            audit_payload = {
                "actor_id": str(actor.get("id", "system")),
                "actor_email": actor.get("email"),
                "actor_role": str(actor.get("role", "SYSTEM")),
                "action": action.upper(),
                "collection": collection,
                "doc_id": str(doc_id),
                "before": before,
                "after": after,
                "timestamp": datetime.now(timezone("UTC")).strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                ),
            }
            return await self._audit_crud.create(audit_payload)
        except Exception as error:
            logging.error(f"Error in AuditService.log_mutation: {error}")
            raise


_audit_service_instance: AuditService | None = None


def get_audit_service() -> AuditService:
    """Retrieve global AuditService singleton instance."""
    global _audit_service_instance
    if _audit_service_instance is None:
        _audit_service_instance = AuditService()
    return _audit_service_instance


# ====== IDEMPOTENCY SERVICE ======

class IdempotencyService:
    """Service facade enforcing idempotent request execution."""

    async def lock_key(self, key: str, endpoint: str, actor_id: str) -> bool:
        """
        Attempt to claim and store an idempotency key.

        Args:
            key (str): Idempotency key string from request header.
            endpoint (str): Endpoint path executing request.
            actor_id (str): ID of user executing request.

        Returns:
            bool: True if key claim was successful.

        Raises:
            HTTPException 409: If idempotency key was already claimed (duplicate request).
        """
        try:
            logging.info(f"Executing IdempotencyService.lock_key for key: {key}")
            db = MongoDatabase()
            doc = {
                "key": key.strip(),
                "endpoint": endpoint,
                "actor_id": actor_id,
                "timestamp": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
            await db.idempotency_keys.insert_one(doc)
            logging.info(f"Idempotency key locked successfully: {key}")
            return True
        except DuplicateKeyError:
            logging.warning(f"Idempotency conflict: key {key} already processed")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate request detected for idempotency key '{key}'. Request already processed.",
            )
        except Exception as error:
            logging.error(f"Error in IdempotencyService.lock_key: {error}")
            raise


_idempotency_service_instance: IdempotencyService | None = None


def get_idempotency_service() -> IdempotencyService:
    """Retrieve global IdempotencyService instance."""
    global _idempotency_service_instance
    if _idempotency_service_instance is None:
        _idempotency_service_instance = IdempotencyService()
    return _idempotency_service_instance
