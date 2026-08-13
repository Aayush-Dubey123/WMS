"""
ticket_router.py — Ticket barcode scanning, inspection approval, and storage assignment routes.

Exposes endpoints for scanning item barcodes, submitting for inspection, manager approval queue,
and assigning storage locations.
"""

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    UploadFile,
    status,
)

from commons.auth import get_current_user
from core import logger
from core.apis.schemas.requests.item_request import ItemLogRequest
from core.apis.schemas.requests.storage_request import StoreTicketRequest
from core.apis.schemas.responses.item_response import ItemResponse
from core.apis.schemas.responses.ticket_response import (
    TicketResponse,
)
from core.controllers.ticket_controller import TicketController
from core.services.storage_service import get_storage_service

ticket_router = APIRouter(tags=["Ticketing, Inspection & Storage"])
logging = logger(__name__)


@ticket_router.post(
    "/tickets/{ticket_id}/items",
    status_code=status.HTTP_201_CREATED,
    response_model=ItemResponse,
)
async def log_item_scan(
    ticket_id: str,
    request: ItemLogRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", description="Unique idempotency lock string"),
    current_user: dict = Depends(get_current_user),
):
    """
    Log a scanned item unit under a ticket (requires Idempotency-Key header).

    Enforces Idempotency-Key header to prevent duplicate item creation on retries.

    Args:
        ticket_id (str): Ticket ID string (e.g. RNO-20260813-001).
        request (ItemLogRequest): Item barcode scanning details.
        idempotency_key (str): Idempotency key from header.
        current_user (dict): Authenticated staff user dependency.

    Returns:
        ItemResponse: Created item unit object.

    Raises:
        HTTPException 400: Missing idempotency key.
        HTTPException 404: Ticket not found.
        HTTPException 409: Duplicate idempotency request.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /tickets/{ticket_id}/items endpoint")
        response = await TicketController().log_item_scan(
            ticket_id=ticket_id,
            item_data=request.model_dump(),
            idempotency_key=idempotency_key,
            current_user=current_user,
        )
        return ItemResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /tickets/{ticket_id}/items endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /tickets/{ticket_id}/items endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@ticket_router.put(
    "/tickets/{id}/submit-inspection",
    status_code=status.HTTP_200_OK,
    response_model=TicketResponse,
)
async def submit_inspection(
    id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Submit completed ticket item logging for Manager inspection review.

    Transitions ticket status to PENDING_INSPECTION.

    Args:
        id (str): Ticket ID string.
        current_user (dict): Authenticated user dependency.

    Returns:
        TicketResponse: Updated ticket object.

    Raises:
        HTTPException 404: Ticket not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling PUT /tickets/{id}/submit-inspection endpoint")
        response = await TicketController().submit_inspection(
            ticket_id=id,
            current_user=current_user,
        )
        return TicketResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in PUT /tickets/{id}/submit-inspection endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in PUT /tickets/{id}/submit-inspection endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )



@ticket_router.post(
    "/tickets/{id}/store",
    status_code=status.HTTP_200_OK,
    response_model=TicketResponse,
)
async def store_ticket(
    id: str,
    request: StoreTicketRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Assign storage location code to ticket and attached items (transitions to STORED).

    Args:
        id (str): Ticket ID string.
        request (StoreTicketRequest): Storage location payload.
        current_user (dict): Authenticated user dependency.

    Returns:
        TicketResponse: Updated ticket object with assigned storage location.

    Raises:
        HTTPException 404: Ticket not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /tickets/{id}/store endpoint")
        response = await TicketController().store_ticket(
            ticket_id=id,
            location_code=request.storage_location,
            current_user=current_user,
        )
        return TicketResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /tickets/{id}/store endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /tickets/{id}/store endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@ticket_router.post(
    "/uploads",
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload item photo image file.

    Args:
        file (UploadFile): Image file stream (.jpg, .png, .webp).
        current_user (dict): Authenticated user dependency.

    Returns:
        dict: Image relative access URL.

    Raises:
        HTTPException 400: Invalid file extension format.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /uploads endpoint")
        image_url = await get_storage_service().save_image(file=file)
        return {"image_url": image_url}
    except HTTPException as httperror:
        logging.error(f"Error in POST /uploads endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /uploads endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
