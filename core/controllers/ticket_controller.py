"""
ticket_controller.py — Controller for ticket inspection, barcode scanning, manager approval, and storage.

Coordinates item barcode scanning (idempotent), Rookie submission, Manager inspection approval, and storage location assignment.
"""

from datetime import datetime

from fastapi import HTTPException, status
from pytz import timezone

from core import logger
from core.cruds.item_crud import CRUDItem
from core.cruds.storage_crud import CRUDStorageLocation
from core.cruds.ticket_crud import CRUDTicket
from core.models.ticket_model import TicketStatus
from core.services.audit_service import get_audit_service
from core.services.idempotency_service import get_idempotency_service

logging = logger(__name__)


class TicketController:
    """Controller managing ticket scanning, inspection approval, and storage placement."""

    def __init__(self):
        """Initialize TicketController with CRUD handlers and services."""
        self._ticket_crud = CRUDTicket()
        self._item_crud = CRUDItem()
        self._storage_crud = CRUDStorageLocation()
        self._audit_service = get_audit_service()
        self._idempotency_service = get_idempotency_service()

    async def log_item_scan(
        self,
        ticket_id: str,
        item_data: dict,
        idempotency_key: str,
        current_user: dict,
    ) -> dict:
        """
        Log barcode item scan payload under a ticket (idempotent).

        Enforces Idempotency-Key header to prevent duplicate logging on retries.

        Args:
            ticket_id (str): Target ticket ID string (e.g. RNO-20260813-001).
            item_data (dict): Item barcode scanning details.
            idempotency_key (str): Idempotency key header value.
            current_user (dict): Authenticated staff user dictionary.

        Returns:
            dict: Created item record payload.

        Raises:
            HTTPException 404: If ticket not found.
            HTTPException 409: Duplicate idempotency key lock.
        """
        try:
            logging.info(f"Executing TicketController.log_item_scan for ticket: {ticket_id}")
            if not idempotency_key:
                logging.warning("Item scan rejected: missing Idempotency-Key header")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Idempotency-Key header is required for item logging",
                )

            # Claim idempotency lock
            await self._idempotency_service.lock_key(
                key=idempotency_key,
                endpoint=f"/tickets/{ticket_id}/items",
                actor_id=str(current_user["id"]),
            )

            ticket = await self._ticket_crud.get_by_ticket_id(ticket_id=ticket_id)
            if not ticket:
                ticket = await self._ticket_crud.get_by_id(id=ticket_id)

            if not ticket:
                logging.warning(f"Item scan failed: ticket {ticket_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ticket '{ticket_id}' not found",
                )

            unit_seq = await self._item_crud.get_next_unit_seq(ticket_id=ticket["ticket_id"])
            damage_input = item_data.get("damage", {})
            is_damaged = damage_input.get("flag", False) if isinstance(damage_input, dict) else False

            item_payload = {
                "ticket_id": ticket["ticket_id"],
                "unit_seq": unit_seq,
                "barcode": item_data.get("barcode", "").strip(),
                "product_name": item_data.get("product_name", "").strip(),
                "width": float(item_data.get("width", 0.0)),
                "height": float(item_data.get("height", 0.0)),
                "weight": float(item_data.get("weight", 0.0)),
                "image_url": item_data.get("image_url"),
                "damage": {
                    "flag": is_damaged,
                    "note": damage_input.get("note") if isinstance(damage_input, dict) else None,
                },
                "status": TicketStatus.DAMAGED.value if is_damaged else TicketStatus.PENDING_INSPECTION.value,
                "warehouse_id": ticket["warehouse_id"],
                "storage_location": None,
                "order_id": None,
                "logged_by": str(current_user["id"]),
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_item = await self._item_crud.create(item_payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="SCAN_ITEM",
                collection="items",
                doc_id=created_item["id"],
                before=None,
                after=created_item,
            )
            logging.info(f"Item scanned and logged successfully! Unit Seq: {unit_seq} under Ticket: {ticket['ticket_id']}")
            return created_item
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in TicketController.log_item_scan: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def submit_inspection(self, ticket_id: str, current_user: dict) -> dict:
        """
        Submit ticket inspection for Manager review (Rookie/Staff action).

        Transitions ticket status to PENDING_INSPECTION.

        Args:
            ticket_id (str): Ticket ID or ticket_id string.
            current_user (dict): Authenticated staff user dictionary.

        Returns:
            dict: Updated ticket dictionary.

        Raises:
            HTTPException 404: Ticket not found.
        """
        try:
            logging.info(f"Executing TicketController.submit_inspection for: {ticket_id}")
            ticket = await self._ticket_crud.get_by_ticket_id(ticket_id=ticket_id)
            if not ticket:
                ticket = await self._ticket_crud.get_by_id(id=ticket_id)

            if not ticket:
                logging.warning(f"Ticket inspection submit failed: ticket {ticket_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticket not found",
                )

            updated = await self._ticket_crud.update(
                id=ticket["id"],
                update_in={
                    "status": TicketStatus.PENDING_INSPECTION.value,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )
            await self._audit_service.log_mutation(
                actor=current_user,
                action="SUBMIT_INSPECTION",
                collection="tickets",
                doc_id=ticket["id"],
                before=ticket,
                after=updated,
            )
            logging.info(f"Ticket submitted for inspection approval: {ticket['ticket_id']}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in TicketController.submit_inspection: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_approvals(self, current_user: dict, skip: int = 0, limit: int = 100) -> dict:
        """
        Retrieve queue of tickets pending inspection approval (Manager only).

        Args:
            current_user (dict): Authenticated manager user dictionary.
            skip (int): Offset count.
            limit (int): Maximum records.

        Returns:
            dict: Dictionary with pending tickets list and total count.
        """
        try:
            logging.info("Executing TicketController.list_approvals")
            filter_query = {"status": TicketStatus.PENDING_INSPECTION.value}
            if current_user.get("warehouse_id"):
                filter_query["warehouse_id"] = current_user.get("warehouse_id")

            pending_tickets, total = await self._ticket_crud.list_tickets(
                filter_query=filter_query, skip=skip, limit=limit
            )
            return {"pending_tickets": pending_tickets, "total": total}
        except Exception as error:
            logging.error(f"Error in TicketController.list_approvals: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def approve_ticket(self, ticket_id: str, current_user: dict) -> dict:
        """
        Approve ticket inspection (Manager only).

        Transitions ticket and attached non-damaged items to SHIPMENT_ARRIVED state (sellable stock).

        Args:
            ticket_id (str): Target ticket ID string.
            current_user (dict): Authenticated Manager dictionary.

        Returns:
            dict: Approved ticket dictionary payload.

        Raises:
            HTTPException 404: Ticket not found.
        """
        try:
            logging.info(f"Executing TicketController.approve_ticket: {ticket_id}")
            ticket = await self._ticket_crud.get_by_ticket_id(ticket_id=ticket_id)
            if not ticket:
                ticket = await self._ticket_crud.get_by_id(id=ticket_id)

            if not ticket:
                logging.warning(f"Ticket approval failed: ticket {ticket_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticket not found",
                )

            updated = await self._ticket_crud.update(
                id=ticket["id"],
                update_in={
                    "status": TicketStatus.SHIPMENT_ARRIVED.value,
                    "approved_by": str(current_user["id"]),
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )

            # Transition non-damaged items to SHIPMENT_ARRIVED
            await self._item_crud.update_status_by_ticket(
                ticket_id=ticket["ticket_id"],
                status_value=TicketStatus.SHIPMENT_ARRIVED.value,
            )

            await self._audit_service.log_mutation(
                actor=current_user,
                action="APPROVE_SHIPMENT",
                collection="tickets",
                doc_id=ticket["id"],
                before=ticket,
                after=updated,
            )
            logging.info(f"Ticket inspection APPROVED! Status: SHIPMENT_ARRIVED for Ticket: {ticket['ticket_id']}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in TicketController.approve_ticket: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def store_ticket(self, ticket_id: str, location_code: str, current_user: dict) -> dict:
        """
        Assign storage location to ticket and transition to STORED state.

        Args:
            ticket_id (str): Ticket ID string.
            location_code (str): Storage location code (e.g. A-04-12).
            current_user (dict): Authenticated staff/manager user dictionary.

        Returns:
            dict: Updated ticket dictionary.

        Raises:
            HTTPException 404: Ticket or storage location not found.
        """
        try:
            logging.info(f"Executing TicketController.store_ticket: {ticket_id} -> {location_code}")
            ticket = await self._ticket_crud.get_by_ticket_id(ticket_id=ticket_id)
            if not ticket:
                ticket = await self._ticket_crud.get_by_id(id=ticket_id)

            if not ticket:
                logging.warning(f"Ticket store failed: ticket {ticket_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticket not found",
                )

            updated = await self._ticket_crud.update(
                id=ticket["id"],
                update_in={
                    "status": TicketStatus.STORED.value,
                    "storage_location": location_code.strip().upper(),
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )

            # Update items storage location and status
            items = await self._item_crud.get_items_by_ticket(ticket_id=ticket["ticket_id"])
            for item in items:
                if not item.get("damage", {}).get("flag", False):
                    await self._item_crud.update_item(
                        id=item["id"],
                        update_in={
                            "status": TicketStatus.STORED.value,
                            "storage_location": location_code.strip().upper(),
                            "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                        },
                    )

            await self._audit_service.log_mutation(
                actor=current_user,
                action="STORE_TICKET",
                collection="tickets",
                doc_id=ticket["id"],
                before=ticket,
                after=updated,
            )
            logging.info(f"Ticket STORED successfully at location: {location_code}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in TicketController.store_ticket: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
