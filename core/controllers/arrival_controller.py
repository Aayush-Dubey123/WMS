"""
arrival_controller.py — Controller for warehouse arrival logging and ticket sequence assignment.

Matches incoming parcel tracking numbers to accepted pre-announcements,
or flags unannounced arrivals (no_ticket_arrival=true), generating atomic ticket IDs.
"""

from datetime import datetime

from fastapi import HTTPException, status
from pytz import timezone

from core import logger
from core.cruds.facility_crud import CRUDWarehouse
from core.cruds.inbox_crud import CRUDInbox
from core.cruds.ticket_crud import CRUDTicket
from core.models.ticket_model import TicketStatus
from core.services.audit_service import get_audit_service
from core.utils.ticket_generator import ticket_generator

logging = logger(__name__)


class ArrivalController:
    """Controller managing parcel arrival and atomic ticket generation."""

    def __init__(self):
        """Initialize ArrivalController with CRUD handlers and services."""
        self._inbox_crud = CRUDInbox()
        self._ticket_crud = CRUDTicket()
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

    async def process_arrival(self, arrival_data: dict, current_user: dict) -> dict:
        """
        Process physical parcel arrival at a warehouse facility.

        Matches tracking number to accepted inbox pre-announcement or flags unannounced arrival,
        and generates an atomic ticket ID ({WH}-{YYYYMMDD}-{SEQ:03d}).

        Args:
            arrival_data (dict): Arrival parameters (warehouse_id, tracking_number, no_ticket_arrival).
            current_user (dict): Authenticated staff user dictionary.

        Returns:
            dict: Created Ticket document payload.

        Raises:
            HTTPException 404: If target warehouse does not exist.
            HTTPException 500: Internal server error.
        """
        try:
            logging.info("Executing ArrivalController.process_arrival")
            wh_id = arrival_data.get("warehouse_id")
            warehouse = await self._wh_crud.get_by_id(id=wh_id)
            if not warehouse:
                logging.warning(f"Arrival processing failed: warehouse {wh_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target warehouse facility not found",
                )

            tracking = arrival_data.get("tracking_number")
            no_ticket_flag = arrival_data.get("no_ticket_arrival", False)
            matched_inbox = None

            if tracking and not no_ticket_flag:
                matched_inbox = await self._inbox_crud.get_by_tracking(tracking_number=tracking.strip())

            if not matched_inbox and not no_ticket_flag and tracking:
                # If tracking was supplied but no pre-announcement matched, mark as unannounced arrival
                no_ticket_flag = True

            ticket_id_str = await ticket_generator.generate_ticket_id(wh_code=warehouse["code"])

            ticket_payload = {
                "ticket_id": ticket_id_str,
                "warehouse_id": wh_id,
                "inbox_id": matched_inbox["id"] if matched_inbox else None,
                "tracking_number": tracking.strip() if tracking else None,
                "no_ticket_arrival": no_ticket_flag,
                "status": TicketStatus.ARRIVED.value,
                "arrived_by": str(current_user["id"]),
                "approved_by": None,
                "storage_location": None,
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_ticket = await self._ticket_crud.create(ticket_payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="ARRIVE",
                collection="tickets",
                doc_id=created_ticket["id"],
                before=None,
                after=created_ticket,
            )
            logging.info(f"Arrival processed successfully! Generated Ticket ID: {ticket_id_str}")
            return created_ticket
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in ArrivalController.process_arrival: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
