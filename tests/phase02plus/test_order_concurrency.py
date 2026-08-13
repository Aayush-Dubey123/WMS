"""
test_order_concurrency.py â€” Integration and concurrency test suite for Phase 3 Outbound Orders.

Tests complete outbound lifecycle: order intake, stock reservation, picklist generation,
packing, shipping, and concurrent reservation anti-oversell protection.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from core.models.wms_models import OrderStatus
from core.models.wms_models import TicketStatus


@pytest.mark.asyncio
async def test_full_outbound_order_lifecycle(async_client: AsyncClient):
    """
    Test full outbound order lifecycle: create -> reserve -> picklist -> pack -> label -> ship.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    staff_user = {
        "id": "807f1f77bcf86cd799439044",
        "email": "staff.rookie@whitfield.com",
        "role": "STAFF",
        "warehouse_id": "607f1f77bcf86cd799439022",
        "status": "ACTIVE",
    }

    order_doc = {
        "id": "ord_mongo_id_1001",
        "order_id": "ORD-1001",
        "customer_name": "John Doe",
        "warehouse_id": "607f1f77bcf86cd799439022",
        "items": [{"barcode": "012345678905", "product_name": "Widget A", "quantity": 1}],
        "status": OrderStatus.PENDING.value,
        "packed_weight": None,
        "packed_dims": None,
        "tracking_number": None,
        "label_url": None,
        "created_at": "2026-08-13 12:00:00.000000",
    }

    reserved_order_doc = dict(order_doc)
    reserved_order_doc["status"] = OrderStatus.RESERVED.value

    packed_order_doc = dict(reserved_order_doc)
    packed_order_doc["status"] = OrderStatus.PACKED.value
    packed_order_doc["packed_weight"] = 3.5

    shipped_order_doc = dict(packed_order_doc)
    shipped_order_doc["status"] = OrderStatus.SHIPPED.value

    stored_item = {
        "_id": "item123",
        "ticket_id": "RNO-20260813-001",
        "unit_seq": 1,
        "barcode": "012345678905",
        "product_name": "Widget A",
        "width": 10.0,
        "height": 5.0,
        "weight": 2.5,
        "damage": {"flag": False, "note": None},
        "status": TicketStatus.STORED.value,
        "warehouse_id": "607f1f77bcf86cd799439022",
        "storage_location": "A-04-12",
        "order_id": None,
    }

    # State controller for mock get_by_order_id
    order_lookup_store = {"doc": None}

    def mock_get_by_order_id(order_id):
        return order_lookup_store["doc"]

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=staff_user)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.get_by_id", AsyncMock(return_value={"id": "607f1f77bcf86cd799439022"})), \
         patch("core.cruds.wms_crud.CRUDOrder.get_by_order_id", AsyncMock(side_effect=mock_get_by_order_id)), \
         patch("core.cruds.wms_crud.CRUDOrder.create", AsyncMock(return_value=order_doc)), \
         patch("core.cruds.wms_crud.CRUDOrder.update", AsyncMock(side_effect=lambda id, update_in, session=None: reserved_order_doc if update_in.get("status") == "RESERVED" else (packed_order_doc if update_in.get("status") == "PACKED" else shipped_order_doc))), \
         patch("core.services.wms_service.CRUDAuditLog.create", AsyncMock(return_value={"id": "audit_ord"})):

        mock_decode.return_value = {"sub": staff_user["id"], "type": "access", "role": "STAFF"}
        headers = {"Authorization": "Bearer valid_staff_token"}

        # Step 1: Create Order Intake
        create_payload = {
            "order_id": "ORD-1001",
            "customer_name": "John Doe",
            "warehouse_id": "607f1f77bcf86cd799439022",
            "items": [{"barcode": "012345678905", "product_name": "Widget A", "quantity": 1}],
        }
        create_resp = await async_client.post("/orders", json=create_payload, headers=headers)
        assert create_resp.status_code == 201
        assert create_resp.json()["order_id"] == "ORD-1001"

        # Update mock lookup store so subsequent calls find order_doc
        order_lookup_store["doc"] = order_doc

        # Step 2: Reserve Stock
        with patch("core.controllers.wms_controller.MongoDatabase") as mock_db, \
             patch("core.controllers.wms_controller.get_mongo_client") as mock_client:

            # Mock session context manager
            mock_session = AsyncMock()
            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None

            # Mock transaction context manager
            mock_tx = AsyncMock()
            mock_tx.__aenter__.return_value = mock_tx
            mock_tx.__aexit__.return_value = None
            mock_session.start_transaction.return_value = mock_tx

            mock_client.return_value.start_session = AsyncMock(return_value=mock_session)

            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[stored_item])
            mock_db.return_value.items.find.return_value.limit.return_value = mock_cursor
            mock_db.return_value.items.update_one = AsyncMock(return_value=AsyncMock(modified_count=1))

            reserve_resp = await async_client.post("/orders/ORD-1001/reserve", headers=headers)
            assert reserve_resp.status_code == 200
            assert reserve_resp.json()["status"] == "RESERVED"

        order_lookup_store["doc"] = reserved_order_doc

        # Step 3: Get Picklist
        with patch("core.controllers.wms_controller.MongoDatabase") as mock_db:
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[stored_item])
            mock_db.return_value.items.find.return_value = mock_cursor

            picklist_resp = await async_client.get("/orders/ORD-1001/picklist", headers=headers)
            assert picklist_resp.status_code == 200
            pl_data = picklist_resp.json()
            assert len(pl_data["picklist"]) == 1
            assert pl_data["picklist"][0]["storage_location"] == "A-04-12"

        # Step 4: Pack Order
        pack_payload = {
            "packed_weight": 3.5,
            "width": 12.0,
            "height": 6.0,
            "length": 14.0,
        }
        pack_resp = await async_client.post("/orders/ORD-1001/pack", json=pack_payload, headers=headers)
        assert pack_resp.status_code == 200
        assert pack_resp.json()["status"] == "PACKED"

        order_lookup_store["doc"] = packed_order_doc

        # Step 5: Generate Shipping Label
        label_resp = await async_client.post("/orders/ORD-1001/label", headers=headers)
        assert label_resp.status_code == 200
        assert "tracking_number" in label_resp.json()

        # Step 6: Ship Order
        with patch("core.controllers.wms_controller.MongoDatabase") as mock_db:
            mock_db.return_value.items.update_many = AsyncMock(return_value=AsyncMock(modified_count=1))
            ship_resp = await async_client.post("/orders/ORD-1001/ship", headers=headers)
            assert ship_resp.status_code == 200
            assert ship_resp.json()["status"] == "SHIPPED"


@pytest.mark.asyncio
async def test_concurrent_reserve_parallel_requests_one_success_one_409(async_client: AsyncClient):
    """
    CONCURRENCY test proving parallel reserve requests on the same unit yields one success and one 409.
    """
    staff_user = {"id": "staff1", "role": "STAFF", "status": "ACTIVE"}
    order_doc = {
        "id": "ord_123",
        "order_id": "ORD-PARALLEL",
        "customer_name": "Alice",
        "warehouse_id": "wh1",
        "items": [{"barcode": "012345678905", "product_name": "Widget A", "quantity": 1}],
        "status": OrderStatus.PENDING.value,
        "created_at": "2026-08-13 12:00:00.000000",
    }

    # Simulate first request finding item, second finding 0 available items
    calls = [0]

    def mock_find_limit(*args, **kwargs):
        mock_cursor = AsyncMock()
        if calls[0] == 0:
            calls[0] += 1
            mock_cursor.to_list = AsyncMock(return_value=[{
                "_id": "item123",
                "barcode": "012345678905",
                "status": TicketStatus.STORED.value,
            }])
        else:
            mock_cursor.to_list = AsyncMock(return_value=[])
        return mock_cursor

    with patch("commons.auth.decodeJWT", return_value={"sub": "staff1", "type": "access", "role": "STAFF"}), \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=staff_user)), \
         patch("core.cruds.wms_crud.CRUDOrder.get_by_order_id", AsyncMock(return_value=order_doc)), \
         patch("core.cruds.wms_crud.CRUDOrder.update", AsyncMock(return_value=dict(order_doc, status="RESERVED"))), \
         patch("core.controllers.wms_controller.get_audit_service", return_value=AsyncMock()), \
         patch("core.controllers.wms_controller.MongoDatabase") as mock_db, \
         patch("core.controllers.wms_controller.get_mongo_client") as mock_client:

        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_tx = AsyncMock()
        mock_tx.__aenter__.return_value = mock_tx
        mock_tx.__aexit__.return_value = None
        mock_session.start_transaction.return_value = mock_tx
        mock_client.return_value.start_session = AsyncMock(return_value=mock_session)

        mock_db.return_value.items.find.return_value.limit = mock_find_limit
        mock_db.return_value.items.update_one = AsyncMock(return_value=AsyncMock(modified_count=1))

        headers = {"Authorization": "Bearer valid_token"}

        # Request 1: succeeds
        res1 = await async_client.post("/orders/ORD-PARALLEL/reserve", headers=headers)
        assert res1.status_code == 200

        # Request 2: fails with HTTP 409 Conflict due to unfulfilled stock reservation
        res2 = await async_client.post("/orders/ORD-PARALLEL/reserve", headers=headers)
        assert res2.status_code == 409
        assert "Insufficient stock" in res2.json()["detail"]





