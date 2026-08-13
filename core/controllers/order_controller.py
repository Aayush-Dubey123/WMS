"""
order_controller.py — Controller for order intake, atomic stock reservation, picklist generation, packing, and shipping.

Implements MongoDB transactions for atomic stock reservation (STORED -> RESERVED) to prevent overselling,
picklist generation, shipping label generation, shipping (RESERVED -> SOLD), and reservation cancellation release.
"""

import uuid
from datetime import datetime

from fastapi import HTTPException, status
from pymongo.errors import OperationFailure, PyMongoError
from pytz import timezone

from core import logger
from core.cruds.facility_crud import CRUDWarehouse
from core.cruds.item_crud import CRUDItem
from core.cruds.order_crud import CRUDOrder
from core.database.database import MongoDatabase, get_mongo_client
from core.models.order_model import OrderStatus
from core.models.ticket_model import TicketStatus
from core.services.audit_service import get_audit_service

logging = logger(__name__)


class OrderController:
    """Controller managing order intake, reservation transactions, pick/pack, and outbound shipping."""

    def __init__(self):
        """Initialize OrderController with CRUD handlers and AuditService."""
        self._order_crud = CRUDOrder()
        self._item_crud = CRUDItem()
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

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
                        if res.modified_count == 0:
                            if session:
                                await session.abort_transaction()
                            logging.warning(f"Concurrent update conflict on item unit {item['_id']}")
                            raise HTTPException(
                                status_code=status.HTTP_409_CONFLICT,
                                detail="Stock unit was modified concurrently by another request",
                            )
                        reserved_item_ids.append(str(item["_id"]))

                updated_order = await self._order_crud.update(
                    id=order["id"],
                    update_in={
                        "status": OrderStatus.RESERVED.value,
                        "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    },
                    session=session,
                )

                if session:
                    await session.commit_transaction()

            except (PyMongoError, OperationFailure) as mongo_err:
                if session:
                    await session.abort_transaction()
                logging.warning(f"MongoDB transaction error during reservation: {mongo_err}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Concurrent reservation conflict detected. Please retry request.",
                )
            finally:
                if session:
                    await session.end_session()

            await self._audit_service.log_mutation(
                actor=current_user,
                action="RESERVE_ORDER",
                collection="orders",
                doc_id=order["id"],
                before=order,
                after=updated_order,
            )
            logging.info(f"Order stock reserved successfully! Order ID: {order['order_id']}")
            return updated_order
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.reserve_order: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_picklist(self, order_id: str, current_user: dict) -> dict:
        """
        Generate picklist containing physical storage bin locations for reserved order items.

        Args:
            order_id (str): Order ID reference.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Picklist details dictionary.

        Raises:
            HTTPException 404: Order not found.
        """
        try:
            logging.info(f"Executing OrderController.get_picklist for: {order_id}")
            db = MongoDatabase()
            order = await self._order_crud.get_by_order_id(order_id=order_id)
            if not order:
                order = await self._order_crud.get_by_id(id=order_id)

            if not order:
                logging.warning(f"Picklist generation failed: order {order_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer order not found",
                )

            cursor = db.items.find({"order_id": order["order_id"]})
            reserved_items = await cursor.to_list(length=1000)

            picklist_items = [
                {
                    "item_id": str(item["_id"]),
                    "ticket_id": item["ticket_id"],
                    "unit_seq": item["unit_seq"],
                    "barcode": item["barcode"],
                    "product_name": item["product_name"],
                    "storage_location": item.get("storage_location", "UNASSIGNED"),
                }
                for item in reserved_items
            ]

            return {
                "order_id": order["order_id"],
                "warehouse_id": order["warehouse_id"],
                "picklist": picklist_items,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.get_picklist: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def pack_order(self, order_id: str, pack_data: dict, current_user: dict) -> dict:
        """
        Confirm packed order weight and package dimensions (transitions status to PACKED).

        Args:
            order_id (str): Order ID reference.
            pack_data (dict): Packing data (packed_weight, width, height, length).
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Updated order payload.

        Raises:
            HTTPException 404: Order not found.
        """
        try:
            logging.info(f"Executing OrderController.pack_order for: {order_id}")
            order = await self._order_crud.get_by_order_id(order_id=order_id)
            if not order:
                order = await self._order_crud.get_by_id(id=order_id)

            if not order:
                logging.warning(f"Pack order failed: order {order_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer order not found",
                )

            dims = {
                "width": float(pack_data.get("width", 0.0)),
                "height": float(pack_data.get("height", 0.0)),
                "length": float(pack_data.get("length", 0.0)),
            }

            updated = await self._order_crud.update(
                id=order["id"],
                update_in={
                    "status": OrderStatus.PACKED.value,
                    "packed_weight": float(pack_data.get("packed_weight", 0.0)),
                    "packed_dims": dims,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )

            await self._audit_service.log_mutation(
                actor=current_user,
                action="PACK_ORDER",
                collection="orders",
                doc_id=order["id"],
                before=order,
                after=updated,
            )
            logging.info(f"Order PACKED successfully: {order['order_id']}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.pack_order: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def generate_label(self, order_id: str, current_user: dict) -> dict:
        """
        Generate carrier shipping label stub for packed order.

        Args:
            order_id (str): Target order ID string.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Shipping label details dictionary.

        Raises:
            HTTPException 404: Order not found.
        """
        try:
            logging.info(f"Executing OrderController.generate_label for: {order_id}")
            order = await self._order_crud.get_by_order_id(order_id=order_id)
            if not order:
                order = await self._order_crud.get_by_id(id=order_id)

            if not order:
                logging.warning(f"Label generation failed: order {order_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer order not found",
                )

            tracking = f"1Z999{uuid.uuid4().hex[:10].upper()}"
            label_url = f"/labels/{order['order_id']}_{tracking}.pdf"

            await self._order_crud.update(
                id=order["id"],
                update_in={
                    "tracking_number": tracking,
                    "label_url": label_url,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )

            logging.info(f"Shipping label generated stub for order {order['order_id']}: {tracking}")
            return {
                "order_id": order["order_id"],
                "carrier": "Carrier Integration Stub (EasyPost/Shippo)",
                "tracking_number": tracking,
                "label_url": label_url,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.generate_label: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def ship_order(self, order_id: str, current_user: dict) -> dict:
        """
        Ship customer order and transition item units to SOLD state.

        Updates order status to SHIPPED and attached item units status to SOLD.

        Args:
            order_id (str): Order ID string.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Updated order payload.

        Raises:
            HTTPException 404: Order not found.
        """
        try:
            logging.info(f"Executing OrderController.ship_order for: {order_id}")
            db = MongoDatabase()
            order = await self._order_crud.get_by_order_id(order_id=order_id)
            if not order:
                order = await self._order_crud.get_by_id(id=order_id)

            if not order:
                logging.warning(f"Ship order failed: order {order_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer order not found",
                )

            # Update attached item units status RESERVED -> SOLD
            await db.items.update_many(
                {"order_id": order["order_id"]},
                {
                    "$set": {
                        "status": TicketStatus.SOLD.value,
                        "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    }
                },
            )

            updated = await self._order_crud.update(
                id=order["id"],
                update_in={
                    "status": OrderStatus.SHIPPED.value,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )

            await self._audit_service.log_mutation(
                actor=current_user,
                action="SHIP_ORDER",
                collection="orders",
                doc_id=order["id"],
                before=order,
                after=updated,
            )
            logging.info(f"Order SHIPPED successfully! Units converted to SOLD: {order['order_id']}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.ship_order: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def cancel_order(self, order_id: str, current_user: dict) -> dict:
        """
        Cancel order reservation and release items back to STORED status.

        Releases reserved units back to STORED status and detaches order_id.

        Args:
            order_id (str): Order ID string.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Updated order payload.

        Raises:
            HTTPException 404: Order not found.
        """
        try:
            logging.info(f"Executing OrderController.cancel_order for: {order_id}")
            db = MongoDatabase()
            order = await self._order_crud.get_by_order_id(order_id=order_id)
            if not order:
                order = await self._order_crud.get_by_id(id=order_id)

            if not order:
                logging.warning(f"Cancel order failed: order {order_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer order not found",
                )

            # Release reserved items back to STORED
            await db.items.update_many(
                {"order_id": order["order_id"], "status": TicketStatus.RESERVED.value},
                {
                    "$set": {
                        "status": TicketStatus.STORED.value,
                        "order_id": None,
                        "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    }
                },
            )

            updated = await self._order_crud.update(
                id=order["id"],
                update_in={
                    "status": OrderStatus.CANCELLED.value,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )

            await self._audit_service.log_mutation(
                actor=current_user,
                action="CANCEL_ORDER",
                collection="orders",
                doc_id=order["id"],
                before=order,
                after=updated,
            )
            logging.info(f"Order CANCELLED successfully! Items released back to STORED: {order['order_id']}")
            return updated
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in OrderController.cancel_order: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
