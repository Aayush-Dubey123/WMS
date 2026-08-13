"""
audit_router.py — Audit log query endpoint routes.

Exposes GET /audit for viewing immutable system mutation audit records.
"""


from fastapi import APIRouter, Depends, HTTPException, Query, status

from commons.auth import require_roles
from core import logger
from core.apis.schemas.responses.audit_response import AuditLogListResponse
from core.controllers.wms_controller import AuditController

audit_router = APIRouter(prefix="/audit", tags=["Audit Log"])
logging = logger(__name__)


@audit_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AuditLogListResponse,
)
async def get_audit_logs(
    actor_id: str | None = Query(None, description="Filter by actor user ID"),
    collection: str | None = Query(None, description="Filter by target collection name"),
    action: str | None = Query(None, description="Filter by action name (CREATE, UPDATE, DELETE)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Retrieve system audit log records (Owner and Manager roles only).

    Args:
        actor_id (Optional[str]): Actor ID filter.
        collection (Optional[str]): Target collection filter.
        action (Optional[str]): Action name filter.
        skip (int): Offset count.
        limit (int): Maximum records.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        AuditLogListResponse: List of audit log records and total count.

    Raises:
        HTTPException 403: Prohibited for Staff role.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling GET /audit endpoint")
        response = await AuditController().get_audit_logs(
            current_user=current_user,
            actor_id=actor_id,
            collection=collection,
            action=action,
            skip=skip,
            limit=limit,
        )
        return AuditLogListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /audit endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /audit endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
