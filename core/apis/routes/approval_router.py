"""
approval_router.py — Manager inspection approval queue and approval action routes.

Exposes GET /approvals (list pending tickets) and POST /tickets/{id}/approve
endpoints for manager review and approval of inspected shipments.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from commons.auth import require_roles
from core import logger
from core.apis.schemas.responses.ticket_response import (
    ApprovalQueueResponse,
    TicketResponse,
)
from core.controllers.ticket_controller import TicketController

approval_router = APIRouter(tags=["Approval Queue"])
logging = logger(__name__)


@approval_router.get(
    "/approvals",
    status_code=status.HTTP_200_OK,
    response_model=ApprovalQueueResponse,
)
async def list_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Retrieve manager queue of tickets pending inspection approval (Manager/Owner only).

    Args:
        skip (int): Pagination offset.
        limit (int): Maximum items.
        current_user (dict): Authenticated user (MANAGER or OWNER).

    Returns:
        ApprovalQueueResponse: List of pending tickets.
    """
    try:
        logging.info("Calling GET /approvals endpoint")
        response = await TicketController().list_approvals(
            current_user=current_user,
            skip=skip,
            limit=limit,
        )
        return ApprovalQueueResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /approvals endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /approvals endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@approval_router.post(
    "/tickets/{id}/approve",
    status_code=status.HTTP_200_OK,
    response_model=TicketResponse,
)
async def approve_ticket(
    id: str,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Approve ticket inspection (Manager/Owner only).

    Transitions ticket and non-damaged items to SHIPMENT_ARRIVED (sellable stock).

    Args:
        id (str): Ticket ID string.
        current_user (dict): Authenticated user (MANAGER or OWNER).

    Returns:
        TicketResponse: Approved ticket object.

    Raises:
        HTTPException 404: Ticket not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /tickets/{id}/approve endpoint")
        response = await TicketController().approve_ticket(
            ticket_id=id,
            current_user=current_user,
        )
        return TicketResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /tickets/{id}/approve endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /tickets/{id}/approve endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
