"""
audit_controller.py — Controller for audit log queries.

Provides filterable audit log retrieval for Owner and Manager roles.
"""


from fastapi import HTTPException, status

from core import logger
from core.cruds.audit_crud import CRUDAuditLog

logging = logger(__name__)


class AuditController:
    """Controller managing audit log query requests."""

    def __init__(self):
        """Initialize AuditController with CRUDAuditLog persistence handler."""
        self._audit_crud = CRUDAuditLog()

    async def get_audit_logs(
        self,
        current_user: dict,
        actor_id: str | None = None,
        collection: str | None = None,
        action: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        """
        Query audit logs filterable by actor ID, target collection, and action name.

        Args:
            current_user (dict): Authenticated user dictionary (OWNER or MANAGER).
            actor_id (Optional[str]): Optional actor ID filter string.
            collection (Optional[str]): Optional target collection filter string.
            action (Optional[str]): Optional action filter string (e.g. CREATE, UPDATE, DELETE).
            skip (int): Pagination offset skip count.
            limit (int): Maximum records to return.

        Returns:
            dict: Dictionary with list of audit log objects and total count.
        """
        try:
            logging.info("Executing AuditController.get_audit_logs")
            filter_query = {}
            if actor_id:
                filter_query["actor_id"] = actor_id
            if collection:
                filter_query["collection"] = collection
            if action:
                filter_query["action"] = action.upper()

            logs, total = await self._audit_crud.list_logs(
                filter_query=filter_query, skip=skip, limit=limit
            )
            return {"logs": logs, "total": total}
        except Exception as error:
            logging.error(f"Error in AuditController.get_audit_logs: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
