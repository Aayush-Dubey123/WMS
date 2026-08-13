"""
test_inbound_flow.py â€” Integration test suite for Phase 2 Inbound Lifecycle.

Tests full flow: pre-announcement -> manager acceptance -> arrival ticket generation ->
idempotent item scanning -> inspection submission -> manager approval -> storage assignment.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from core.models.wms_models import InboxStatus
from core.models.wms_models import TicketStatus


@pytest.mark.asyncio
async def test_end_to_end_inbound_flow(async_client: AsyncClient):
    """
    Test complete end-to-end inbound lifecycle from announcement to storage assignment.

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

    manager_user = {
        "id": "707f1f77bcf86cd799439033",
        "email": "manager.rno@whitfield.com",
        "role": "MANAGER",
        "warehouse_id": "607f1f77bcf86cd799439022",
        "status": "ACTIVE",
    }

    wh_doc = {
        "id": "607f1f77bcf86cd799439022",
        "code": "RNO",
        "name": "Reno Warehouse",
    }

    inbox_doc = {
        "id": "inbox123",
        "seller_name": "Acme Corp",
        "expected_items": [{"name": "Widget A", "quantity": 10}],
        "tracking_number": "1Z9999999999999999",
        "carrier": "UPS",
        "warehouse_id": "607f1f77bcf86cd799439022",
        "status": InboxStatus.ACCEPTED.value,
        "comments": [],
        "created_at": "2026-08-13 12:00:00.000000",
    }

    ticket_doc = {
        "id": "ticket123",
        "ticket_id": "RNO-20260813-001",
        "warehouse_id": "607f1f77bcf86cd799439022",
        "inbox_id": "inbox123",
        "tracking_number": "1Z9999999999999999",
        "no_ticket_arrival": False,
        "status": TicketStatus.ARRIVED.value,
        "arrived_by": staff_user["id"],
        "approved_by": None,
        "storage_location": None,
        "created_at": "2026-08-13 12:00:00.000000",
    }

    item_doc = {
        "id": "item123",
        "ticket_id": "RNO-20260813-001",
        "unit_seq": 1,
        "barcode": "012345678905",
        "product_name": "Widget A",
        "width": 10.0,
        "height": 5.0,
        "weight": 2.5,
        "image_url": None,
        "damage": {"flag": False, "note": None},
        "status": TicketStatus.PENDING_INSPECTION.value,
        "warehouse_id": "607f1f77bcf86cd799439022",
        "storage_location": None,
        "order_id": None,
        "logged_by": staff_user["id"],
        "created_at": "2026-08-13 12:00:00.000000",
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(side_effect=lambda id: staff_user if id == staff_user["id"] else manager_user)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.get_by_id", AsyncMock(return_value=wh_doc)), \
         patch("core.cruds.wms_crud.CRUDInbox.get_by_tracking", AsyncMock(return_value=inbox_doc)), \
         patch("core.controllers.wms_controller.ticket_generator.generate_ticket_id", AsyncMock(return_value="RNO-20260813-001")), \
         patch("core.cruds.wms_crud.CRUDTicket.create", AsyncMock(return_value=ticket_doc)), \
         patch("core.cruds.wms_crud.CRUDTicket.get_by_ticket_id", AsyncMock(return_value=ticket_doc)), \
         patch("core.cruds.wms_crud.CRUDTicket.update", AsyncMock(return_value=ticket_doc)), \
         patch("core.cruds.wms_crud.CRUDItem.get_next_unit_seq", AsyncMock(return_value=1)), \
         patch("core.cruds.wms_crud.CRUDItem.create", AsyncMock(return_value=item_doc)), \
         patch("core.cruds.wms_crud.CRUDItem.get_items_by_ticket", AsyncMock(return_value=[item_doc])), \
         patch("core.cruds.wms_crud.CRUDItem.update_status_by_ticket", AsyncMock(return_value=1)), \
         patch("core.cruds.wms_crud.CRUDItem.update_item", AsyncMock(return_value=item_doc)), \
         patch("core.services.wms_service.IdempotencyService.lock_key", AsyncMock(return_value=True)), \
         patch("core.services.wms_service.CRUDAuditLog.create", AsyncMock(return_value={"id": "audit_ok"})):

        mock_decode.return_value = {"sub": staff_user["id"], "type": "access", "role": "STAFF"}

        headers = {"Authorization": "Bearer valid_staff_token"}

        # Step 1: Process Arrival
        arrival_payload = {
            "warehouse_id": "607f1f77bcf86cd799439022",
            "tracking_number": "1Z9999999999999999",
            "no_ticket_arrival": False,
        }
        resp = await async_client.post("/arrivals", json=arrival_payload, headers=headers)
        assert resp.status_code == 201
        arr_data = resp.json()
        assert arr_data["ticket_id"] == "RNO-20260813-001"

        # Step 2: Log Scanned Item with Idempotency-Key
        scan_headers = {
            "Authorization": "Bearer valid_staff_token",
            "Idempotency-Key": "idemp_scan_001_seq_1",
        }
        item_payload = {
            "barcode": "012345678905",
            "product_name": "Widget A",
            "width": 10.0,
            "height": 5.0,
            "weight": 2.5,
        }
        item_resp = await async_client.post("/tickets/RNO-20260813-001/items", json=item_payload, headers=scan_headers)
        assert item_resp.status_code == 201
        item_data_resp = item_resp.json()
        assert item_data_resp["unit_seq"] == 1

        # Step 3: Submit Inspection
        submit_resp = await async_client.put("/tickets/ticket123/submit-inspection", headers=headers)
        assert submit_resp.status_code == 200

        # Step 4: Manager Approves Ticket
        mock_decode.return_value = {"sub": manager_user["id"], "type": "access", "role": "MANAGER"}
        mgr_headers = {"Authorization": "Bearer valid_manager_token"}
        approve_resp = await async_client.post("/tickets/ticket123/approve", headers=mgr_headers)
        assert approve_resp.status_code == 200

        # Step 5: Store Ticket
        store_payload = {"storage_location": "A-04-12"}
        store_resp = await async_client.post("/tickets/ticket123/store", json=store_payload, headers=mgr_headers)
        assert store_resp.status_code == 200


@pytest.mark.asyncio
async def test_unannounced_arrival_no_ticket_flag(async_client: AsyncClient):
    """
    Test parcel arrival flagged as unannounced (no_ticket_arrival=true).

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    staff_user = {
        "id": "807f1f77bcf86cd799439044",
        "email": "staff.rookie@whitfield.com",
        "role": "STAFF",
        "status": "ACTIVE",
    }

    wh_doc = {
        "id": "wh_unannounced",
        "code": "LAX",
        "name": "LAX Facility",
    }

    unannounced_ticket = {
        "id": "ticket_unannounced",
        "ticket_id": "LAX-20260813-001",
        "warehouse_id": "wh_unannounced",
        "inbox_id": None,
        "tracking_number": None,
        "no_ticket_arrival": True,
        "status": TicketStatus.ARRIVED.value,
        "arrived_by": staff_user["id"],
        "approved_by": None,
        "storage_location": None,
        "created_at": "2026-08-13 12:00:00.000000",
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=staff_user)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.get_by_id", AsyncMock(return_value=wh_doc)), \
         patch("core.controllers.wms_controller.ticket_generator.generate_ticket_id", AsyncMock(return_value="LAX-20260813-001")), \
         patch("core.cruds.wms_crud.CRUDTicket.create", AsyncMock(return_value=unannounced_ticket)), \
         patch("core.services.wms_service.CRUDAuditLog.create", AsyncMock(return_value={"id": "audit_arr"})):

        mock_decode.return_value = {"sub": staff_user["id"], "type": "access", "role": "STAFF"}
        headers = {"Authorization": "Bearer valid_staff_token"}

        arrival_payload = {
            "warehouse_id": "wh_unannounced",
            "no_ticket_arrival": True,
        }
        resp = await async_client.post("/arrivals", json=arrival_payload, headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["no_ticket_arrival"] is True
        assert data["ticket_id"].startswith("LAX-")


@pytest.mark.asyncio
async def test_duplicate_submission_idempotency(async_client: AsyncClient):
    """
    Test duplicate submission with the same Idempotency-Key raises 409 conflict when locked.
    """
    staff_user = {"id": "staff1", "role": "STAFF", "status": "ACTIVE"}
    from fastapi import HTTPException

    with patch("commons.auth.decodeJWT", return_value={"sub": "staff1", "type": "access", "role": "STAFF"}), \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=staff_user)), \
         patch("core.cruds.wms_crud.CRUDTicket.get_by_ticket_id", AsyncMock(return_value={"id": "t1", "ticket_id": "RNO-20260813-001", "status": "ARRIVED", "warehouse_id": "wh1"})), \
         patch("core.controllers.wms_controller.get_idempotency_service", return_value=AsyncMock(lock_key=AsyncMock(side_effect=HTTPException(status_code=409, detail="Duplicate submission")))), \
         patch("core.controllers.wms_controller.get_audit_service", return_value=AsyncMock()):

        headers = {
            "Authorization": "Bearer valid_token",
            "Idempotency-Key": "dup_key_12345",
        }
        item_payload = {
            "barcode": "012345678905",
            "product_name": "Widget A",
            "width": 10.0,
            "height": 5.0,
            "weight": 2.5,
        }
        resp = await async_client.post("/tickets/RNO-20260813-001/items", json=item_payload, headers=headers)
        assert resp.status_code == 409
        assert "Duplicate submission" in resp.json()["detail"]





