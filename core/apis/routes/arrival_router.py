"""
arrival_router.py — Physical arrival logging endpoint routes.

Exposes POST /arrivals for logging parcel arrivals and generating atomic ticket IDs.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from commons.auth import get_current_user
from core import logger
from core.apis.schemas.requests.arrival_request import ArrivalCreateRequest
from core.apis.schemas.responses.ticket_response import TicketResponse
from core.controllers.wms_controller import ArrivalController

arrival_router = APIRouter(prefix="/arrivals", tags=["Arrivals & Ticketing"])
logging = logger(__name__)


@arrival_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TicketResponse,
)
async def process_arrival(
    request: ArrivalCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Log physical parcel arrival at a warehouse facility.

    Matches carrier tracking number to an accepted inbox announcement or flags no_ticket_arrival=true,
    generating an atomic ticket ID ({WH}-{YYYYMMDD}-{SEQ:03d}).

    Args:
        request (ArrivalCreateRequest): Arrival payload (warehouse_id, tracking_number, no_ticket_arrival).
        current_user (dict): Authenticated user (staff member).

    Returns:
        TicketResponse: Created Ticket object.

    Raises:
        HTTPException 404: Warehouse not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /arrivals endpoint")
        response = await ArrivalController().process_arrival(
            arrival_data=request.model_dump(),
            current_user=current_user,
        )
        return TicketResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /arrivals endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /arrivals endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
