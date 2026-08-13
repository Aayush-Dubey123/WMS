"""
inbox_controller.py — Controller for inbox shipment announcements and approval actions.

Manages parcel announcement creation, acceptance, rejection, and comment threading for NEEDS_SPEC.
"""

from datetime import datetime

from fastapi import HTTPException, status
from pytz import timezone

from core import logger
from core.cruds.facility_crud import CRUDWarehouse
from core.cruds.inbox_crud import CRUDInbox
from core.models.inbox_model import InboxStatus
from core.services.audit_service import get_audit_service

logging = logger(__name__)


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
            comment_text (str): Comment text describing requested specifications.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Updated inbox shipment document.

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

            comment_doc = {
                "user_id": str(current_user["id"]),
                "user_email": current_user.get("email"),
                "comment": comment_text,
                "timestamp": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            await self._inbox_crud.add_comment(id=inbox_id, comment_doc=comment_doc)
            updated = await self._inbox_crud.update(
                id=inbox_id,
                update_in={
                    "status": InboxStatus.NEEDS_SPEC.value,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )
            await self._audit_service.log_mutation(
                actor=current_user,
                action="REVERT_NEEDS_SPEC",
                collection="inbox_shipments",
                doc_id=inbox_id,
                before=before,
                after=updated,
            )
            logging.info(f"Inbox shipment reverted to NEEDS_SPEC: {inbox_id}")
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
        List inbox shipment announcements filterable by status and scoped by role.

        Args:
            current_user (dict): Authenticated user dictionary.
            status_filter (Optional[str]): Optional status filter string.
            skip (int): Offset count.
            limit (int): Maximum records.

        Returns:
            dict: Dictionary with list of shipments and total count.
        """
        try:
            logging.info("Executing InboxController.list_shipments")
            filter_query = {}
            if current_user.get("role") == "MANAGER" and current_user.get("warehouse_id"):
                filter_query["warehouse_id"] = current_user.get("warehouse_id")

            if status_filter:
                filter_query["status"] = status_filter.upper()

            shipments, total = await self._inbox_crud.list_shipments(filter_query=filter_query, skip=skip, limit=limit)
            return {"shipments": shipments, "total": total}
        except Exception as error:
            logging.error(f"Error in InboxController.list_shipments: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
