"""
audit_service.py — Service layer for system mutation audit logging.

Provides automatic audit trail recording for database mutations across all services.
"""

from datetime import datetime
from typing import Any

from pytz import timezone

from core import logger
from core.cruds.audit_crud import CRUDAuditLog

logging = logger(__name__)


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
            # Audit service must log failure without swallowing if required, or return fallback
            raise


_audit_service_instance: AuditService | None = None


def get_audit_service() -> AuditService:
    """
    Retrieve global AuditService singleton instance.

    Returns:
        AuditService: Configured audit service instance.
    """
    global _audit_service_instance
    if _audit_service_instance is None:
        _audit_service_instance = AuditService()
    return _audit_service_instance
