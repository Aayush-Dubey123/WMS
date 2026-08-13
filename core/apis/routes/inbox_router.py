"""
inbox_router.py — Seller pre-announcement inbox endpoint routes.

Exposes endpoints for seller parcel announcements, manager acceptance, rejection, and comment threading.
"""


from fastapi import APIRouter, Depends, HTTPException, Query, status

from commons.auth import get_current_user, require_roles
from core import logger
from core.apis.schemas.requests.inbox_request import (
    InboxAnnounceRequest,
    InboxRevertRequest,
)
from core.apis.schemas.responses.inbox_response import InboxListResponse, InboxResponse
from core.controllers.inbox_controller import InboxController

inbox_router = APIRouter(prefix="/inbox", tags=["Inbox & Announcements"])
logging = logger(__name__)


@inbox_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=InboxResponse,
)
async def announce_shipment(
    request: InboxAnnounceRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Announce an incoming parcel shipment (status ANNOUNCED).

    Args:
        request (InboxAnnounceRequest): Parcel announcement payload.
        current_user (dict): Authenticated user dictionary.

    Returns:
        InboxResponse: Created inbox shipment object.

    Raises:
        HTTPException 404: Warehouse not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /inbox endpoint")
        response = await InboxController().announce_shipment(
            shipment_data=request.model_dump(),
            current_user=current_user,
        )
        return InboxResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /inbox endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /inbox endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@inbox_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=InboxListResponse,
)
async def list_shipments(
    status_filter: str | None = Query(None, alias="status", description="Filter by status (ANNOUNCED, ACCEPTED, DECLINED, NEEDS_SPEC)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
):
    """
    List inbox shipment announcements filterable by status.

    Args:
        status_filter (Optional[str]): Status filter string.
        skip (int): Pagination offset.
        limit (int): Maximum records.
        current_user (dict): Authenticated user dependency.

    Returns:
        InboxListResponse: List of inbox shipments.
    """
    try:
        logging.info("Calling GET /inbox endpoint")
        response = await InboxController().list_shipments(
            current_user=current_user,
            status_filter=status_filter,
            skip=skip,
            limit=limit,
        )
        return InboxListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /inbox endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /inbox endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@inbox_router.post(
    "/{id}/accept",
    status_code=status.HTTP_200_OK,
    response_model=InboxResponse,
)
async def accept_shipment(
    id: str,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Accept an inbox shipment announcement (Manager/Owner only).

    Args:
        id (str): Inbox shipment ID string.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        InboxResponse: Updated inbox shipment object.

    Raises:
        HTTPException 404: Shipment not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /inbox/{id}/accept endpoint")
        response = await InboxController().accept_shipment(inbox_id=id, current_user=current_user)
        return InboxResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /inbox/{id}/accept endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /inbox/{id}/accept endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@inbox_router.post(
    "/{id}/decline",
    status_code=status.HTTP_200_OK,
    response_model=InboxResponse,
)
async def decline_shipment(
    id: str,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Decline an inbox shipment announcement (Manager/Owner only).

    Args:
        id (str): Inbox shipment ID string.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        InboxResponse: Updated inbox shipment object.

    Raises:
        HTTPException 404: Shipment not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /inbox/{id}/decline endpoint")
        response = await InboxController().decline_shipment(inbox_id=id, current_user=current_user)
        return InboxResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /inbox/{id}/decline endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /inbox/{id}/decline endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@inbox_router.post(
    "/{id}/revert",
    status_code=status.HTTP_200_OK,
    response_model=InboxResponse,
)
async def revert_shipment(
    id: str,
    request: InboxRevertRequest,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Revert an inbox shipment to NEEDS_SPEC state with comment (Manager/Owner only).

    Args:
        id (str): Inbox shipment ID string.
        request (InboxRevertRequest): Revert comment payload.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        InboxResponse: Updated inbox shipment object with comment thread.

    Raises:
        HTTPException 404: Shipment not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /inbox/{id}/revert endpoint")
        response = await InboxController().revert_shipment(
            inbox_id=id,
            comment_text=request.comment,
            current_user=current_user,
        )
        return InboxResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /inbox/{id}/revert endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /inbox/{id}/revert endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
