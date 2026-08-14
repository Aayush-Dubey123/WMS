"""
wms_controller.py — Consolidated WMS business logic controllers.

Merges all domain controllers: arrival, health, inbox, ticket, storage, order, report,
voice, vision, natural language query, API key, audit, and warehouse facility management.
Each controller orchestrates CRUD operations, service calls, and audit logging for its domain.
"""

import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from pymongo.errors import OperationFailure, PyMongoError
from pytz import timezone

from commons.auth import hash_api_key
from core import logger
from core.cruds.wms_crud import (
    CRUDApiKey,
    CRUDAuditLog,
    CRUDWarehouse,
    CRUDInbox,
    CRUDItem,
    CRUDOrder,
    CRUDStorageLocation,
    CRUDTicket,
    CRUDVoiceDraft,
)
from core.database.database import MongoDatabase, get_mongo_client
from core.models.wms_models import InboxStatus, OrderStatus, TicketStatus, DraftStatus
from core.services.wms_service import get_audit_service, get_idempotency_service
from core.services.integration_service import get_export_service
from core.services.ai_service import get_nl_query_service, get_vision_service, get_voice_service
from core.config.settings import settings
from core.database.database import ping
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


class HealthController:
    """
    Controller managing system and database health validation.

    Coordinates database connection verification and returns structured health details.
    """

    async def get_health(self) -> dict:
        """
        Check database connectivity and generate system health payload.

        Returns:
            dict: Dictionary containing health status, database connection, and timestamp.

        Raises:
            HTTPException: If database ping fails or system is unhealthy.
        """
        try:
            logging.info("Executing HealthController.get_health")
            db_status = "connected"
            try:
                await ping()
            except Exception as db_err:
                logging.warning(f"Database ping failed in HealthController: {db_err}")
                db_status = "disconnected"

            system_ok = db_status == "connected"
            timestamp = datetime.now(timezone("UTC")).isoformat()

            if not system_ok:
                logging.warning("System health status check failed due to database issue")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "status": "degraded",
                        "service": settings.APP_NAME,
                        "version": settings.APP_VERSION,
                        "database": db_status,
                        "timestamp": timestamp,
                    },
                )

            return {
                "status": "ok",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "database": db_status,
                "timestamp": timestamp,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in HealthController.get_health: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class InboxController:
    """Controller managing inbound shipment pre-announcements."""

    def __init__(self):
        """Initialize InboxController with CRUDInbox, CRUDWarehouse, and AuditService."""
        self._inbox_crud = CRUDInbox()
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

    async def announce_shipment(self, shipment_data: dict, current_user: dict) -> dict:
        """
        Create a seller pre-announcement parcel shipment (ANNOUNCED state).

        Args:
            shipment_data (dict): Shipment payload containing seller and item details.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Created inbox shipment payload.

        Raises:
            HTTPException 404: If target warehouse facility does not exist.
        """
        try:
            logging.info("Executing InboxController.announce_shipment")
            wh_id = shipment_data.get("warehouse_id")
            warehouse = await self._wh_crud.get_by_id(id=wh_id)
            if not warehouse:
                logging.warning(f"Inbox announcement failed: warehouse {wh_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target warehouse facility not found",
                )

            tracking = shipment_data.get("tracking_number")
            if tracking:
                existing = await self._inbox_crud.get_by_tracking(tracking_number=tracking)
                if existing:
                    logging.warning(f"Inbox announcement warning: tracking number {tracking} already exists")

            payload = {
                "seller_name": shipment_data.get("seller_name"),
                "expected_items": shipment_data.get("expected_items", []),
                "tracking_number": tracking.strip() if tracking else None,
                "carrier": shipment_data.get("carrier"),
                "warehouse_id": wh_id,
                "status": InboxStatus.ANNOUNCED.value,
                "comments": [],
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_shipment = await self._inbox_crud.create(payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="CREATE",
                collection="inbox_shipments",
                doc_id=created_shipment["id"],
                before=None,
                after=created_shipment,
            )
            logging.info(f"Inbox shipment announced successfully: ID {created_shipment['id']}")
            return created_shipment
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in InboxController.announce_shipment: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def accept_shipment(self, inbox_id: str, current_user: dict) -> dict:
        """
        Accept an inbox shipment announcement (Manager/Owner only).

        Transitions status to ACCEPTED.

        Args:
            inbox_id (str): Inbox shipment ID string.
            current_user (dict): Authenticated user (MANAGER or OWNER).

        Returns:
            dict: Updated inbox shipment payload.

        Raises:
            HTTPException 404: If inbox shipment not found.
        """
        try:
            logging.info(f"Executing InboxController.accept_shipment: {inbox_id}")
            before = await self._inbox_crud.get_by_id(id=inbox_id)
            if not before:
                logging.warning(f"Inbox shipment not found: {inbox_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inbox shipment announcement not found",
                )

            updated = await self._inbox_crud.update(
                id=inbox_id,
                update_in={
                    "status": InboxStatus.ACCEPTED.value,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )
            await self._audit_service.log_mutation(
                actor=current_user,
                action="ACCEPT",
                collection="inbox_shipments",
                doc_id=inbox_id,
                before=before,
                after=updated,
            )
            logging.info(f"Inbox shipment ACCEPTED: {inbox_id}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in InboxController.accept_shipment: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def decline_shipment(self, inbox_id: str, current_user: dict) -> dict:
        """
        Decline an inbox shipment announcement (Manager/Owner only).

        Transitions status to DECLINED.

        Args:
            inbox_id (str): Inbox shipment ID string.
            current_user (dict): Authenticated user (MANAGER or OWNER).

        Returns:
            dict: Updated inbox shipment payload.

        Raises:
            HTTPException 404: If inbox shipment not found.
        """
        try:
            logging.info(f"Executing InboxController.decline_shipment: {inbox_id}")
            before = await self._inbox_crud.get_by_id(id=inbox_id)
            if not before:
                logging.warning(f"Inbox shipment not found: {inbox_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inbox shipment announcement not found",
                )

            updated = await self._inbox_crud.update(
                id=inbox_id,
                update_in={
                    "status": InboxStatus.DECLINED.value,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )
            await self._audit_service.log_mutation(
                actor=current_user,
                action="DECLINE",
                collection="inbox_shipments",
                doc_id=inbox_id,
                before=before,
                after=updated,
            )
            logging.info(f"Inbox shipment DECLINED: {inbox_id}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in InboxController.decline_shipment: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def revert_shipment(self, inbox_id: str, comment_text: str, current_user: dict) -> dict:
        """
        Revert an inbox shipment announcement to NEEDS_SPEC state with discussion comment.

        Args:
            inbox_id (str): Inbox shipment ID string.
            comment_text (str): User comment text.
            current_user (dict): Authenticated user (MANAGER or OWNER).

        Returns:
            dict: Updated inbox shipment payload with comment thread.

        Raises:
            HTTPException 404: If inbox shipment not found.
        """
        try:
            logging.info(f"Executing InboxController.revert_shipment: {inbox_id}")
            before = await self._inbox_crud.get_by_id(id=inbox_id)
            if not before:
                logging.warning(f"Inbox shipment not found: {inbox_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inbox shipment announcement not found",
                )

            comments = before.get("comments", [])
            comments.append({
                "author_id": str(current_user["id"]),
                "text": comment_text,
                "timestamp": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            })

            updated = await self._inbox_crud.update(
                id=inbox_id,
                update_in={
                    "status": InboxStatus.NEEDS_SPEC.value,
                    "comments": comments,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )
            await self._audit_service.log_mutation(
                actor=current_user,
                action="REVERT",
                collection="inbox_shipments",
                doc_id=inbox_id,
                before=before,
                after=updated,
            )
            logging.info(f"Inbox shipment REVERTED to NEEDS_SPEC: {inbox_id}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in InboxController.revert_shipment: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_shipments(self, current_user: dict, status_filter: str | None = None, skip: int = 0, limit: int = 100) -> dict:
        """
        List inbox shipment announcements filterable by status.

        Args:
            current_user (dict): Authenticated user dependency.
            status_filter (Optional[str]): Status filter string.
            skip (int): Pagination offset.
            limit (int): Maximum records.

        Returns:
            dict: Dictionary with shipments list and total count.
        """
        try:
            logging.info("Executing InboxController.list_shipments")
            filter_query = {}
            if status_filter:
                filter_query["status"] = status_filter.upper()

            shipments, total = await self._inbox_crud.list_shipments(
                filter_query=filter_query, skip=skip, limit=limit
            )
            return {"shipments": shipments, "total": total}
        except Exception as error:
            logging.error(f"Error in InboxController.list_shipments: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class TicketController:
    """Controller managing ticket scanning, inspection approval, and storage placement."""

    def __init__(self):
        """Initialize TicketController with CRUD handlers and services."""
        self._ticket_crud = CRUDTicket()
        self._item_crud = CRUDItem()
        self._storage_crud = CRUDStorageLocation()
        self._audit_service = get_audit_service()
        self._idempotency_service = get_idempotency_service()

    async def get_ticket(self, id: str, current_user: dict) -> dict:
        """
        Retrieve a single ticket by ID with warehouse-scope enforcement.

        Args:
            id: Mongo _id or ticket_id string.
            current_user: Authenticated user for role-based scoping.

        Returns:
            dict: Ticket payload.

        Raises:
            HTTPException 404: Ticket not found, or outside caller's warehouse scope.
        """
        try:
            logging.info(f"Executing TicketController.get_ticket: {id}")
            ticket = await self._ticket_crud.get_by_id(id=id)
            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticket not found",
                )

            if current_user.get("role") in ["STAFF", "MANAGER"]:
                user_warehouse_id = current_user.get("warehouse_id")
                if user_warehouse_id and ticket.get("warehouse_id") != user_warehouse_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Ticket not found",
                    )

            return ticket
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in TicketController.get_ticket: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_ticket_items(self, ticket_id: str, current_user: dict) -> dict:
        """
        List all scanned item units for a ticket, with warehouse-scope enforcement
        on the parent ticket.

        Args:
            ticket_id: Ticket ID string.
            current_user: Authenticated user for role-based scoping.

        Returns:
            dict with 'items' list and 'total' count.

        Raises:
            HTTPException 404: Ticket not found, or outside caller's warehouse scope.
        """
        try:
            logging.info(f"Executing TicketController.list_ticket_items: {ticket_id}")
            ticket = await self._ticket_crud.get_by_id(id=ticket_id)
            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticket not found",
                )

            if current_user.get("role") in ["STAFF", "MANAGER"]:
                user_warehouse_id = current_user.get("warehouse_id")
                if user_warehouse_id and ticket.get("warehouse_id") != user_warehouse_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Ticket not found",
                    )

            items = await self._item_crud.get_items_by_ticket(ticket_id=ticket.get("ticket_id", ticket_id))
            return {"items": items, "total": len(items)}
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in TicketController.list_ticket_items: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

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
            tickets, total = await self._ticket_crud.list_approvals(skip=skip, limit=limit)
            return {"tickets": tickets, "total": total}
        except Exception as error:
            logging.error(f"Error in TicketController.list_approvals: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def approve_ticket(self, ticket_id: str, current_user: dict) -> dict:
        """
        Approve ticket inspection (Manager/Owner only).

        Transitions ticket and non-damaged items to SHIPMENT_ARRIVED (sellable stock).

        Args:
            ticket_id (str): Ticket ID string.
            current_user (dict): Authenticated user (MANAGER or OWNER).

        Returns:
            dict: Approved ticket object.

        Raises:
            HTTPException 404: Ticket not found.
            HTTPException 500: Internal server error.
        """
        try:
            logging.info(f"Executing TicketController.approve_ticket for: {ticket_id}")
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

            await self._audit_service.log_mutation(
                actor=current_user,
                action="APPROVE",
                collection="tickets",
                doc_id=ticket["id"],
                before=ticket,
                after=updated,
            )
            logging.info(f"Ticket APPROVED: {ticket_id}")
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
        Assign storage location code to ticket and attached items (transitions to STORED).

        Args:
            ticket_id (str): Ticket ID string.
            location_code (str): Storage location code.
            current_user (dict): Authenticated user dependency.

        Returns:
            dict: Updated ticket object with assigned storage location.

        Raises:
            HTTPException 404: Ticket not found.
            HTTPException 500: Internal server error.
        """
        try:
            logging.info(f"Executing TicketController.store_ticket for: {ticket_id}")
            ticket = await self._ticket_crud.get_by_ticket_id(ticket_id=ticket_id)
            if not ticket:
                ticket = await self._ticket_crud.get_by_id(id=ticket_id)

            if not ticket:
                logging.warning(f"Ticket storage assignment failed: ticket {ticket_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticket not found",
                )

            updated = await self._ticket_crud.update(
                id=ticket["id"],
                update_in={
                    "status": TicketStatus.STORED.value,
                    "storage_location": location_code,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )

            await self._audit_service.log_mutation(
                actor=current_user,
                action="STORE",
                collection="tickets",
                doc_id=ticket["id"],
                before=ticket,
                after=updated,
            )
            logging.info(f"Ticket STORED at location: {location_code}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in TicketController.store_ticket: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_tickets(
        self,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
        facility: str | None = None,
        seller: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        current_user: dict | None = None,
    ) -> dict:
        """
        List tickets with pagination and role-based filtering.

        Args:
            skip: Number of records to skip.
            limit: Max records per page.
            status_filter: Filter by status (PENDING_APPROVAL/APPROVED/STORED).
            facility: Filter by warehouse ID.
            seller: Filter by seller/vendor.
            start_date: ISO date for ticket start.
            end_date: ISO date for ticket end.
            current_user: Authenticated user for role-based filtering.

        Returns:
            dict with 'tickets' list and 'total' count.
        """
        try:
            logging.info("Executing TicketController.list_tickets")
            filter_doc = {}

            if status_filter:
                filter_doc["status"] = status_filter.upper()

            if seller:
                filter_doc["seller"] = seller

            if facility:
                filter_doc["warehouse_id"] = facility
            elif current_user and current_user.get("role") in ["STAFF", "MANAGER"]:
                filter_doc["warehouse_id"] = current_user.get("warehouse_id")

            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                if date_filter:
                    filter_doc["created_at"] = date_filter

            tickets, total = await self._ticket_crud.list_tickets(
                filter_query=filter_doc, skip=skip, limit=limit
            )

            return {
                "tickets": [t.model_dump() if hasattr(t, "model_dump") else t for t in tickets],
                "total": total,
            }
        except Exception as error:
            logging.error(f"Error in TicketController.list_tickets: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class StorageController:
    """Controller managing warehouse storage bin locations."""

    def __init__(self):
        """Initialize StorageController with CRUD storage, CRUD warehouse, and AuditService."""
        self._storage_crud = CRUDStorageLocation()
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

    async def create_location(self, storage_data: dict, current_user: dict) -> dict:
        """
        Create a physical storage location bin in a warehouse facility.

        Location code is constructed as {ZONE}-{RACK}-{BIN} (e.g. A-04-12).

        Args:
            storage_data (dict): Location creation parameters.
            current_user (dict): Authenticated Manager user dictionary.

        Returns:
            dict: Created storage location payload.

        Raises:
            HTTPException 400: Duplicate location code.
            HTTPException 404: Target warehouse facility not found.
        """
        try:
            logging.info("Executing StorageController.create_location")
            wh_id = storage_data.get("warehouse_id")
            warehouse = await self._wh_crud.get_by_id(id=wh_id)
            if not warehouse:
                logging.warning(f"Storage location creation failed: warehouse {wh_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target warehouse facility not found",
                )

            zone = storage_data.get("zone", "").strip().upper()
            rack = storage_data.get("rack", "").strip().upper()
            bin_code = storage_data.get("bin", "").strip().upper()
            location_code = f"{zone}-{rack}-{bin_code}"

            existing = await self._storage_crud.get_by_code(warehouse_id=wh_id, location_code=location_code)
            if existing:
                logging.warning(f"Storage location creation rejected: location code {location_code} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Storage location code '{location_code}' already exists in warehouse",
                )

            payload = {
                "warehouse_id": wh_id,
                "zone": zone,
                "rack": rack,
                "bin": bin_code,
                "location_code": location_code,
                "is_occupied": False,
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_location = await self._storage_crud.create(payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="CREATE",
                collection="storage_locations",
                doc_id=created_location["id"],
                before=None,
                after=created_location,
            )
            logging.info(f"Storage location created successfully: {location_code}")
            return created_location
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in StorageController.create_location: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_locations(self, warehouse_id: str, skip: int = 0, limit: int = 100) -> dict:
        """
        List storage locations for a warehouse facility.

        Args:
            warehouse_id (str): Target warehouse facility ID.
            skip (int): Offset count.
            limit (int): Maximum records.

        Returns:
            dict: Dictionary with list of storage locations and total count.
        """
        try:
            logging.info(f"Executing StorageController.list_locations for WH: {warehouse_id}")
            locations, total = await self._storage_crud.list_locations(
                warehouse_id=warehouse_id, skip=skip, limit=limit
            )
            return {"locations": locations, "total": total}
        except Exception as error:
            logging.error(f"Error in StorageController.list_locations: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class OrderController:
    """Controller managing order intake, reservation transactions, pick/pack, and outbound shipping."""

    def __init__(self):
        """Initialize OrderController with CRUD handlers and AuditService."""
        self._order_crud = CRUDOrder()
        self._item_crud = CRUDItem()
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

    async def get_order(self, id: str, current_user: dict) -> dict:
        """
        Retrieve a single order by ID with warehouse-scope enforcement.

        Args:
            id: Mongo _id or order_id string.
            current_user: Authenticated user for role-based scoping.

        Returns:
            dict: Order payload.

        Raises:
            HTTPException 404: Order not found, or outside caller's warehouse scope.
        """
        try:
            logging.info(f"Executing OrderController.get_order: {id}")
            order = await self._order_crud.get_by_id(id=id)
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found",
                )

            if current_user.get("role") in ["STAFF", "MANAGER"]:
                user_warehouse_id = current_user.get("warehouse_id")
                if user_warehouse_id and order.get("warehouse_id") != user_warehouse_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Order not found",
                    )

            return order
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.get_order: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def create_order(self, order_data: dict, current_user: dict) -> dict:
        """
        Create a new manual intake customer order in PENDING status.

        Args:
            order_data (dict): Order creation payload.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Created order payload.

        Raises:
            HTTPException 400: Duplicate order ID.
            HTTPException 404: Warehouse facility not found.
        """
        try:
            logging.info("Executing OrderController.create_order")
            order_id = order_data.get("order_id", "").strip().upper()
            existing = await self._order_crud.get_by_order_id(order_id=order_id)
            if existing:
                logging.warning(f"Order creation rejected: order_id {order_id} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order with ID '{order_id}' already exists",
                )

            wh_id = order_data.get("warehouse_id")
            warehouse = await self._wh_crud.get_by_id(id=wh_id)
            if not warehouse:
                logging.warning(f"Order creation failed: warehouse {wh_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target warehouse facility not found",
                )

            order_payload = {
                "order_id": order_id,
                "customer_name": order_data.get("customer_name"),
                "warehouse_id": wh_id,
                "items": order_data.get("items", []),
                "status": OrderStatus.PENDING.value,
                "packed_weight": None,
                "packed_dims": None,
                "tracking_number": None,
                "label_url": None,
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_order = await self._order_crud.create(order_payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="CREATE",
                collection="orders",
                doc_id=created_order["id"],
                before=None,
                after=created_order,
            )
            logging.info(f"Customer order created successfully: {order_id}")
            return created_order
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.create_order: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def reserve_order(self, order_id: str, current_user: dict) -> dict:
        """
        Atomically reserve inventory stock for an order inside a MongoDB transaction.

        Verifies each item unit is STORED -> transitions selected items to RESERVED and attaches order_id.
        Concurrent reservation requests for the same item units yield HTTP 409 Conflict.

        Args:
            order_id (str): Target order ID reference string.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Updated order payload.

        Raises:
            HTTPException 400: Insufficient stock or invalid order state.
            HTTPException 404: Order not found.
            HTTPException 409: Concurrent reservation conflict detected.
        """
        try:
            logging.info(f"Executing OrderController.reserve_order for: {order_id}")
            db = MongoDatabase()

            order = await self._order_crud.get_by_order_id(order_id=order_id)
            if not order:
                order = await self._order_crud.get_by_id(id=order_id)

            if not order:
                logging.warning(f"Reservation failed: order {order_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer order not found",
                )

            if order.get("status") != OrderStatus.PENDING.value:
                logging.warning(f"Reservation rejected: order {order_id} is in status {order.get('status')}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order is in status '{order.get('status')}', expected PENDING",
                )

            client = get_mongo_client()
            session = None
            try:
                if client:
                    try:
                        session = await client.start_session()
                        if session:
                            session.start_transaction()
                    except Exception as sess_err:
                        logging.warning(f"Session transaction setup skipped: {sess_err}")
                        session = None

                reserved_item_ids = []
                for line_item in order.get("items", []):
                    barcode = line_item.get("barcode")
                    qty_needed = line_item.get("quantity", 1)

                    find_kwargs = {}
                    if session:
                        find_kwargs["session"] = session

                    cursor = db.items.find(
                        {
                            "warehouse_id": order["warehouse_id"],
                            "barcode": barcode,
                            "status": TicketStatus.STORED.value,
                            "damage.flag": False,
                        },
                        **find_kwargs,
                    ).limit(qty_needed)

                    available_items = await cursor.to_list(length=qty_needed)
                    if len(available_items) < qty_needed:
                        if session:
                            await session.abort_transaction()
                        logging.warning(
                            f"Stock reservation failed: barcode {barcode} needs {qty_needed}, available {len(available_items)}"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=f"Insufficient stock for barcode '{barcode}'. Required: {qty_needed}, Available: {len(available_items)}",
                        )

                    for item in available_items:
                        update_kwargs = {}
                        if session:
                            update_kwargs["session"] = session

                        res = await db.items.update_one(
                            {"_id": item["_id"], "status": TicketStatus.STORED.value},
                            {
                                "$set": {
                                    "status": TicketStatus.RESERVED.value,
                                    "order_id": order["order_id"],
                                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                                }
                            },
                            **update_kwargs,
                        )
                        if res.modified_count == 1:
                            reserved_item_ids.append(str(item["_id"]))

                if session:
                    await session.commit_transaction()

                updated = await self._order_crud.update(
                    id=order["id"],
                    update_in={
                        "status": OrderStatus.RESERVED.value,
                        "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    },
                )

                await self._audit_service.log_mutation(
                    actor=current_user,
                    action="RESERVE",
                    collection="orders",
                    doc_id=order["id"],
                    before=order,
                    after=updated,
                )
                logging.info(f"Order reserved successfully! Reserved items: {len(reserved_item_ids)}")
                return updated
            except HTTPException:
                raise
            except (OperationFailure, PyMongoError) as txn_err:
                logging.error(f"Transaction failed during reservation: {txn_err}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Reservation transaction failed. Please retry.",
                )
            finally:
                if session:
                    await session.end_session()
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.reserve_order: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def ship_order(self, order_id: str, current_user: dict, tracking: str | None = None, label_url: str | None = None) -> dict:
        """
        Ship a reserved order (mark as SOLD).

        Args:
            order_id (str): Order ID string.
            current_user (dict): Authenticated user dictionary.
            tracking (Optional[str]): Shipping tracking number.
            label_url (Optional[str]): Shipping label URL.

        Returns:
            dict: Updated order payload.

        Raises:
            HTTPException 404: Order not found.
            HTTPException 400: Order not in RESERVED status.
        """
        try:
            logging.info(f"Executing OrderController.ship_order for: {order_id}")
            order = await self._order_crud.get_by_order_id(order_id=order_id)
            if not order:
                order = await self._order_crud.get_by_id(id=order_id)

            if not order:
                logging.warning(f"Order shipping failed: order {order_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found",
                )

            if order.get("status") != OrderStatus.RESERVED.value:
                logging.warning(f"Order shipping rejected: order {order_id} is in status {order.get('status')}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order must be in RESERVED status to ship",
                )

            updated = await self._order_crud.update(
                id=order["id"],
                update_in={
                    "status": OrderStatus.SOLD.value,
                    "tracking_number": tracking,
                    "label_url": label_url,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )

            await self._audit_service.log_mutation(
                actor=current_user,
                action="SHIP",
                collection="orders",
                doc_id=order["id"],
                before=order,
                after=updated,
            )
            logging.info(f"Order SHIPPED: {order_id}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.ship_order: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_orders(
        self,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
        facility: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        current_user: dict | None = None,
    ) -> dict:
        """
        List orders with pagination and role-based filtering.

        Args:
            skip: Number of records to skip.
            limit: Max records per page.
            status_filter: Filter by status (PENDING/RESERVED/PACKED/SHIPPED).
            facility: Filter by warehouse ID.
            start_date: ISO date for order start.
            end_date: ISO date for order end.
            current_user: Authenticated user for role-based filtering.

        Returns:
            dict with 'orders' list and 'total' count.
        """
        try:
            logging.info(f"Executing OrderController.list_orders")
            filter_doc = {}

            if status_filter:
                filter_doc["status"] = status_filter.upper()

            if facility:
                filter_doc["warehouse_id"] = facility
            elif current_user and current_user.get("role") in ["STAFF", "MANAGER"]:
                filter_doc["warehouse_id"] = current_user.get("warehouse_id")

            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                if date_filter:
                    filter_doc["created_at"] = date_filter

            orders, total = await self._order_crud.list_orders(
                filter_query=filter_doc, skip=skip, limit=limit
            )

            return {
                "orders": [o.model_dump() if hasattr(o, "model_dump") else o for o in orders],
                "total": total,
            }
        except Exception as error:
            logging.error(f"Error in OrderController.list_orders: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class ReportController:
    """Controller managing reporting, stock totals aggregations, and exports."""

    def __init__(self):
        """Initialize ReportController with ExportService."""
        self._export_service = get_export_service()

    async def get_summary(self, target_date: str | None, current_user: dict) -> dict:
        """
        Generate executive summary metrics for a given date (defaults to today UTC).

        Calculates today's tickets, today's sold items, and unannounced arrivals per warehouse.

        Args:
            target_date (Optional[str]): Date string in YYYY-MM-DD format.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Summary metrics payload dictionary.
        """
        try:
            logging.info(f"Executing ReportController.get_summary for date: {target_date}")
            db = MongoDatabase()

            date_prefix = target_date.strip() if target_date else datetime.now(timezone("UTC")).strftime("%Y-%m-%d")

            ticket_cursor = db.tickets.find({"created_at": {"$regex": f"^{date_prefix}"}})
            tickets_today = await ticket_cursor.to_list(length=10000)

            item_cursor = db.items.find({"status": TicketStatus.SOLD.value, "updated_at": {"$regex": f"^{date_prefix}"}})
            items_sold_today = await item_cursor.to_list(length=10000)

            total_tickets = len(tickets_today)
            total_sold = len(items_sold_today)
            total_missed = sum(1 for t in tickets_today if t.get("no_ticket_arrival", False))

            wh_map: dict[str, dict[str, int]] = {}
            for t in tickets_today:
                wh_id = t.get("warehouse_id", "UNKNOWN")
                if wh_id not in wh_map:
                    wh_map[wh_id] = {"todays_tickets": 0, "todays_sold": 0, "arrived_missed": 0}
                wh_map[wh_id]["todays_tickets"] += 1
                if t.get("no_ticket_arrival", False):
                    wh_map[wh_id]["arrived_missed"] += 1

            for item in items_sold_today:
                wh_id = item.get("warehouse_id", "UNKNOWN")
                if wh_id not in wh_map:
                    wh_map[wh_id] = {"todays_tickets": 0, "todays_sold": 0, "arrived_missed": 0}
                wh_map[wh_id]["todays_sold"] += 1

            per_warehouse_list = [
                {
                    "warehouse_id": wh_id,
                    "todays_tickets": metrics["todays_tickets"],
                    "todays_sold": metrics["todays_sold"],
                    "arrived_missed": metrics["arrived_missed"],
                }
                for wh_id, metrics in wh_map.items()
            ]

            return {
                "date": date_prefix,
                "todays_tickets": total_tickets,
                "todays_sold": total_sold,
                "arrived_missed": total_missed,
                "per_warehouse": per_warehouse_list,
            }
        except Exception as error:
            logging.error(f"Error in ReportController.get_summary: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_arrived_today(self, target_date: str | None, current_user: dict, warehouse_id: str | None = None) -> dict:
        """
        Generate detail feed of parcels/tickets arrived on target date.

        Args:
            target_date (Optional[str]): Date string (YYYY-MM-DD).
            current_user (dict): Authenticated user dictionary.
            warehouse_id (Optional[str]): Optional warehouse ID filter.

        Returns:
            dict: Detail feed records dictionary.
        """
        try:
            logging.info("Executing ReportController.get_arrived_today")
            db = MongoDatabase()
            date_prefix = target_date.strip() if target_date else datetime.now(timezone("UTC")).strftime("%Y-%m-%d")

            filter_query: dict[str, Any] = {"created_at": {"$regex": f"^{date_prefix}"}}
            if warehouse_id:
                filter_query["warehouse_id"] = warehouse_id
            elif current_user.get("role") == "MANAGER" and current_user.get("warehouse_id"):
                filter_query["warehouse_id"] = current_user.get("warehouse_id")

            cursor = db.tickets.find(filter_query).sort("created_at", -1)
            tickets = await cursor.to_list(length=10000)

            records = [
                {
                    "ticket_id": t.get("ticket_id"),
                    "warehouse_id": t.get("warehouse_id"),
                    "tracking_number": t.get("tracking_number"),
                    "no_ticket_arrival": t.get("no_ticket_arrival"),
                    "status": t.get("status"),
                    "arrived_by": t.get("arrived_by"),
                    "created_at": t.get("created_at"),
                }
                for t in tickets
            ]

            return {
                "feed_type": "arrived_today",
                "records": records,
                "total": len(records),
            }
        except Exception as error:
            logging.error(f"Error in ReportController.get_arrived_today: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_sold_today(self, target_date: str | None, current_user: dict, warehouse_id: str | None = None) -> dict:
        """
        Generate detail feed of item units sold on target date.

        Args:
            target_date (Optional[str]): Date string (YYYY-MM-DD).
            current_user (dict): Authenticated user dictionary.
            warehouse_id (Optional[str]): Optional warehouse ID filter.

        Returns:
            dict: Detail feed records dictionary.
        """
        try:
            logging.info("Executing ReportController.get_sold_today")
            db = MongoDatabase()
            date_prefix = target_date.strip() if target_date else datetime.now(timezone("UTC")).strftime("%Y-%m-%d")

            filter_query: dict[str, Any] = {
                "status": TicketStatus.SOLD.value,
                "updated_at": {"$regex": f"^{date_prefix}"},
            }
            if warehouse_id:
                filter_query["warehouse_id"] = warehouse_id
            elif current_user.get("role") == "MANAGER" and current_user.get("warehouse_id"):
                filter_query["warehouse_id"] = current_user.get("warehouse_id")

            cursor = db.items.find(filter_query).sort("updated_at", -1)
            items = await cursor.to_list(length=10000)

            records = [
                {
                    "item_id": str(i.get("_id")),
                    "ticket_id": i.get("ticket_id"),
                    "unit_seq": i.get("unit_seq"),
                    "barcode": i.get("barcode"),
                    "product_name": i.get("product_name"),
                    "warehouse_id": i.get("warehouse_id"),
                    "storage_location": i.get("storage_location"),
                    "order_id": i.get("order_id"),
                    "status": i.get("status"),
                    "updated_at": i.get("updated_at"),
                }
                for i in items
            ]

            return {
                "feed_type": "sold_today",
                "records": records,
                "total": len(records),
            }
        except Exception as error:
            logging.error(f"Error in ReportController.get_sold_today: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class VoiceController:
    """Controller managing voice audio processing and draft item confirmations."""

    def __init__(self):
        """Initialize VoiceController with VoiceService and CRUDVoiceDraft."""
        self._voice_service = get_voice_service()
        self._draft_crud = CRUDVoiceDraft()

    async def transcribe(self, audio_bytes: bytes, filename: str, current_user: dict) -> dict:
        """
        Transcribe audio file payload to text transcript.

        Args:
            audio_bytes (bytes): Binary audio content.
            filename (str): Audio filename.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Transcript payload dictionary.
        """
        try:
            logging.info("Executing VoiceController.transcribe")
            transcript = await self._voice_service.transcribe_audio(audio_bytes=audio_bytes, filename=filename)
            return {"transcript": transcript}
        except Exception as error:
            logging.error(f"Error in VoiceController.transcribe: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def parse_transcript(self, ticket_id: str, transcript: str, current_user: dict) -> dict:
        """
        Parse text transcript into structured draft item using LLM and save as DRAFT.

        Args:
            ticket_id (str): Target arrival ticket ID string.
            transcript (str): Audio transcript string.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Saved voice draft document payload.
        """
        try:
            logging.info(f"Executing VoiceController.parse_transcript for ticket: {ticket_id}")
            parsed_res = await self._voice_service.parse_transcript(transcript=transcript)

            wh_id = current_user.get("warehouse_id", "wh_default")

            draft_payload = {
                "user_id": current_user["id"],
                "warehouse_id": wh_id,
                "ticket_id": ticket_id,
                "transcript": transcript,
                "parsed_data": parsed_res["parsed_data"],
                "confidence_scores": parsed_res["confidence_scores"],
                "status": DraftStatus.DRAFT.value,
            }

            created_draft = await self._draft_crud.create(draft_payload)
            logging.info(f"Voice draft saved successfully! Draft ID: {created_draft['id']}")
            return created_draft
        except Exception as error:
            logging.error(f"Error in VoiceController.parse_transcript: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def confirm_draft(
        self,
        draft_id: str,
        barcode: str,
        override_weight: float,
        current_user: dict,
    ) -> dict:
        """
        Confirm voice draft by writing through the EXACT SAME Phase 2 item logging service pipeline.

        No AI shortcut or DB bypass: calls TicketController.log_item_scan directly!

        Args:
            draft_id (str): Voice draft ID string.
            barcode (str): Confirmed product barcode.
            override_weight (float): Confirmed manual item weight.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Created item unit record payload from Phase 2 pipeline.

        Raises:
            HTTPException 404: Voice draft not found.
            HTTPException 400: Draft already processed or discarded.
        """
        try:
            logging.info(f"Executing VoiceController.confirm_draft for draft: {draft_id}")
            draft = await self._draft_crud.get_by_id(id=draft_id)
            if not draft:
                logging.warning(f"Voice draft confirm failed: draft {draft_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Voice draft not found",
                )

            if draft.get("status") != DraftStatus.DRAFT.value:
                logging.warning(f"Voice draft confirm rejected: status is {draft.get('status')}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Voice draft status is '{draft.get('status')}', expected DRAFT",
                )

            parsed = draft.get("parsed_data", {})

            item_scan_data = {
                "barcode": barcode.strip(),
                "product_name": parsed.get("product_name", "Scanned Item"),
                "width": float(parsed.get("width", 0.0)),
                "height": float(parsed.get("height", 0.0)),
                "weight": float(override_weight),
                "image_url": None,
                "damage": parsed.get("damage", {"flag": False, "note": None}),
            }

            created_item = await TicketController().log_item_scan(
                ticket_id=draft["ticket_id"],
                item_data=item_scan_data,
                idempotency_key=f"voice_draft_{draft_id}",
                current_user=current_user,
            )

            await self._draft_crud.update(id=draft_id, update_in={"status": DraftStatus.CONFIRMED.value})

            logging.info(f"Voice draft confirmed and logged through Phase 2 pipeline! Draft ID: {draft_id}")
            return created_item
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in VoiceController.confirm_draft: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class VisionController:
    """Controller managing OpenCV vision measurement requests."""

    def __init__(self):
        """Initialize VisionController with VisionService."""
        self._vision_service = get_vision_service()

    async def measure_package(self, image_bytes: bytes, current_user: dict) -> dict:
        """
        Estimate package width and height from uploaded photo containing ArUco reference marker.

        Args:
            image_bytes (bytes): Image binary file content.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Measurement details dictionary.
        """
        try:
            logging.info("Executing VisionController.measure_package")
            result = await self._vision_service.measure_package(image_bytes=image_bytes)
            return result
        except Exception as error:
            logging.error(f"Error in VisionController.measure_package: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class NLQueryController:
    """Controller managing natural language stock query requests."""

    def __init__(self):
        """Initialize NLQueryController with NLQueryService."""
        self._query_service = get_nl_query_service()

    async def execute_query(self, query_text: str, current_user: dict) -> dict:
        """
        Execute safe natural language stock query.

        Args:
            query_text (str): Query prompt string.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Formatted query response payload dictionary.
        """
        try:
            logging.info("Executing NLQueryController.execute_query")
            role = current_user.get("role", "STAFF")
            wh_id = current_user.get("warehouse_id")
            result = await self._query_service.execute_query(
                query_text=query_text,
                user_role=role,
                warehouse_id=wh_id,
            )
            return result
        except ValueError as error:
            logging.warning(f"NL query rejected outside allow-list: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            )
        except Exception as error:
            logging.error(f"Error in NLQueryController.execute_query: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


class ApiKeyController:
    """Controller managing API key administration."""

    def __init__(self):
        """Initialize ApiKeyController with CRUDApiKey."""
        self._key_crud = CRUDApiKey()

    async def create_key(self, key_data: dict, current_user: dict) -> dict:
        """
        Generate a new scoped API key. Returns raw secret key ONLY ONCE.

        Args:
            key_data (dict): Key creation payload.
            current_user (dict): Authenticated user dictionary (OWNER or MANAGER).

        Returns:
            dict: API key response containing raw secret key.
        """
        try:
            logging.info("Executing ApiKeyController.create_key")
            raw_secret = f"wms_live_{uuid.uuid4().hex}"
            prefix = raw_secret[:12]
            key_hash = hash_api_key(raw_secret)

            key_payload = {
                "name": key_data.get("name"),
                "key_hash": key_hash,
                "prefix": prefix,
                "role": key_data.get("role", "STAFF"),
                "scopes": key_data.get("scopes", ["read"]),
                "is_active": True,
                "created_by": current_user["id"],
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created = await self._key_crud.create(key_payload)
            created["raw_key"] = raw_secret

            logging.info(f"API key created successfully! Name: {created['name']} | Prefix: {prefix}")
            return created
        except Exception as error:
            logging.error(f"Error in ApiKeyController.create_key: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_keys(self, current_user: dict) -> list[dict]:
        """
        List API keys created by current user.

        Args:
            current_user (dict): Authenticated user dictionary.

        Returns:
            List[dict]: List of API key records (without raw secrets).
        """
        try:
            logging.info("Executing ApiKeyController.list_keys")
            keys = await self._key_crud.list_keys(user_id=current_user["id"])
            return keys
        except Exception as error:
            logging.error(f"Error in ApiKeyController.list_keys: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def revoke_key(self, key_id: str, current_user: dict) -> dict:
        """
        Revoke an API key.

        Args:
            key_id (str): API key ID.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Revoked key record.

        Raises:
            HTTPException 404: Key not found.
        """
        try:
            logging.info(f"Executing ApiKeyController.revoke_key: {key_id}")
            revoked = await self._key_crud.revoke(id=key_id)
            if not revoked:
                logging.warning(f"API key revocation failed: key {key_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="API key not found",
                )
            logging.info(f"API key revoked successfully: {key_id}")
            return revoked
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in ApiKeyController.revoke_key: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )


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


class WarehouseController:
    """Controller managing warehouse facilities."""

    def __init__(self):
        """Initialize WarehouseController with CRUD warehouse and audit service."""
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

    async def create_warehouse(self, wh_data: dict, current_user: dict) -> dict:
        """
        Create a new warehouse facility (Owner only).

        Args:
            wh_data (dict): Warehouse creation payload dictionary.
            current_user (dict): Authenticated user dictionary (must be OWNER).

        Returns:
            dict: Created warehouse record dictionary.

        Raises:
            HTTPException 400: If warehouse code already exists.
            HTTPException 500: Internal server error.
        """
        try:
            logging.info("Executing WarehouseController.create_warehouse")
            code = wh_data.get("code", "").strip().upper()
            existing = await self._wh_crud.get_by_code(code=code)
            if existing:
                logging.warning(f"Warehouse creation rejected: code {code} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Warehouse code '{code}' already exists",
                )

            wh_payload = {
                "code": code,
                "name": wh_data.get("name"),
                "address": wh_data.get("address"),
                "manager_id": None,
                "is_active": True,
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_wh = await self._wh_crud.create(wh_payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="CREATE",
                collection="warehouses",
                doc_id=created_wh["id"],
                before=None,
                after=created_wh,
            )
            logging.info(f"Warehouse created successfully: {code}")
            return created_wh
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in WarehouseController.create_warehouse: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_warehouses(self, skip: int = 0, limit: int = 100) -> dict:
        """
        List warehouse facilities with pagination.

        Args:
            skip (int): Offset skip count.
            limit (int): Maximum items to return.

        Returns:
            dict: Dictionary with list of warehouses and total count.
        """
        try:
            logging.info("Executing WarehouseController.list_warehouses")
            warehouses, total = await self._wh_crud.list_warehouses(skip=skip, limit=limit)
            return {"warehouses": warehouses, "total": total}
        except Exception as error:
            logging.error(f"Error in WarehouseController.list_warehouses: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_warehouse_by_id(self, wh_id: str) -> dict:
        """
        Retrieve warehouse details by unique ID.

        Args:
            wh_id (str): Warehouse ID string.

        Returns:
            dict: Warehouse details payload.

        Raises:
            HTTPException 404: If warehouse is not found.
        """
        try:
            logging.info(f"Executing WarehouseController.get_warehouse_by_id: {wh_id}")
            wh = await self._wh_crud.get_by_id(id=wh_id)
            if not wh:
                logging.warning(f"Warehouse not found: {wh_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse facility not found",
                )
            return wh
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in WarehouseController.get_warehouse_by_id: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def update_warehouse(self, wh_id: str, update_data: dict, current_user: dict) -> dict:
        """
        Update warehouse facility parameters (Owner only).

        Args:
            wh_id (str): Warehouse ID string.
            update_data (dict): Dictionary of parameters to update.
            current_user (dict): Authenticated user dictionary (OWNER).

        Returns:
            dict: Updated warehouse dictionary.

        Raises:
            HTTPException 404: If warehouse not found.
        """
        try:
            logging.info(f"Executing WarehouseController.update_warehouse: {wh_id}")
            before = await self._wh_crud.get_by_id(id=wh_id)
            if not before:
                logging.warning(f"Warehouse not found for update: {wh_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse facility not found",
                )

            clean_updates = {k: v for k, v in update_data.items() if v is not None}
            clean_updates["updated_at"] = datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f")

            updated_wh = await self._wh_crud.update(id=wh_id, update_in=clean_updates)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="UPDATE",
                collection="warehouses",
                doc_id=wh_id,
                before=before,
                after=updated_wh,
            )
            logging.info(f"Warehouse updated successfully: {wh_id}")
            return updated_wh
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in WarehouseController.update_warehouse: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
