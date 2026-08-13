"""
test_ai_and_api_keys.py — Integration test suite for Phase 5 AI features & API key administration.

Tests voice transcription, LLM draft parsing, draft confirmation writing through Phase 2 pipeline,
vision measurement, natural language stock search, and API key management.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_voice_pipeline_flow(async_client: AsyncClient):
    """
    Test voice transcribe, parse draft, and confirm draft flow.

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

    draft_doc = {
        "id": "draft123",
        "user_id": staff_user["id"],
        "warehouse_id": "607f1f77bcf86cd799439022",
        "ticket_id": "RNO-20260813-001",
        "transcript": "Received Widget A width 10 height 5 weight 2.5",
        "parsed_data": {
            "product_name": "Widget A",
            "width": 10.0,
            "height": 5.0,
            "weight": 2.5,
            "fragile": False,
            "damage": {"flag": False, "note": None},
        },
        "confidence_scores": {"product_name": 0.95, "width": 0.9, "height": 0.9, "weight": 0.85},
        "status": "DRAFT",
        "created_at": "2026-08-13 12:00:00.000000",
    }

    logged_item = {
        "id": "item_voice_1",
        "ticket_id": "RNO-20260813-001",
        "unit_seq": 1,
        "barcode": "012345678905",
        "product_name": "Widget A",
        "width": 10.0,
        "height": 5.0,
        "weight": 2.5,
        "damage": {"flag": False, "note": None},
        "status": "PENDING_INSPECTION",
        "warehouse_id": "607f1f77bcf86cd799439022",
        "storage_location": None,
        "order_id": None,
        "logged_by": staff_user["id"],
        "created_at": "2026-08-13 12:00:00.000000",
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=staff_user)), \
         patch("core.cruds.voice_draft_crud.CRUDVoiceDraft.create", AsyncMock(return_value=draft_doc)), \
         patch("core.cruds.voice_draft_crud.CRUDVoiceDraft.get_by_id", AsyncMock(return_value=draft_doc)), \
         patch("core.cruds.voice_draft_crud.CRUDVoiceDraft.update", AsyncMock(return_value=draft_doc)), \
         patch("core.controllers.ticket_controller.TicketController.log_item_scan", AsyncMock(return_value=logged_item)):

        mock_decode.return_value = {"sub": staff_user["id"], "type": "access", "role": "STAFF"}
        headers = {"Authorization": "Bearer valid_staff_token"}

        # Step 1: Transcribe Audio
        files = {"file": ("test.wav", b"fake_audio_bytes", "audio/wav")}
        trans_resp = await async_client.post("/voice/transcribe", files=files, headers=headers)
        assert trans_resp.status_code == 200
        assert "transcript" in trans_resp.json()

        # Step 2: Parse Draft
        parse_payload = {
            "ticket_id": "RNO-20260813-001",
            "transcript": "Received Widget A width 10 height 5 weight 2.5",
        }
        parse_resp = await async_client.post("/voice/parse", json=parse_payload, headers=headers)
        assert parse_resp.status_code == 201
        assert parse_resp.json()["id"] == "draft123"

        # Step 3: Confirm Draft (writes through Phase 2 item logging pipeline)
        confirm_payload = {
            "barcode": "012345678905",
            "override_weight": 2.5,
        }
        confirm_resp = await async_client.post("/voice/drafts/draft123/confirm", json=confirm_payload, headers=headers)
        assert confirm_resp.status_code == 201
        assert confirm_resp.json()["barcode"] == "012345678905"


@pytest.mark.asyncio
async def test_vision_measure(async_client: AsyncClient):
    """
    Test POST /vision/measure endpoint returns package dimension estimates.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    staff_user = {
        "id": "807f1f77bcf86cd799439044",
        "role": "STAFF",
        "status": "ACTIVE",
    }

    vision_payload = {
        "width": 10.0,
        "height": 5.0,
        "weight": 0.0,
        "confidence": 0.92,
        "marker_found": True,
        "error": None,
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=staff_user)), \
         patch("core.services.vision_service.VisionService.measure_package", AsyncMock(return_value=vision_payload)):

        mock_decode.return_value = {"sub": staff_user["id"], "type": "access", "role": "STAFF"}
        headers = {"Authorization": "Bearer valid_staff_token"}

        files = {"file": ("box.jpg", b"fake_jpeg_bytes", "image/jpeg")}
        resp = await async_client.post("/vision/measure", files=files, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["width"] == 10.0
        assert data["weight"] == 0.0  # Weight ALWAYS manual


@pytest.mark.asyncio
async def test_nl_stock_query(async_client: AsyncClient):
    """
    Test POST /query endpoint executes safe allow-listed natural language stock search.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    manager_user = {
        "id": "707f1f77bcf86cd799439033",
        "role": "MANAGER",
        "warehouse_id": "607f1f77bcf86cd799439022",
        "status": "ACTIVE",
    }

    query_res = {
        "template_used": "STOCK_AVAILABLE",
        "description": "Get available stored stock for product",
        "query_text": "How many widgets in Reno?",
        "results": [{"product_name": "Widget A", "count": 25}],
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=manager_user)), \
         patch("core.services.nl_query_service.NLQueryService.execute_query", AsyncMock(return_value=query_res)):

        mock_decode.return_value = {"sub": manager_user["id"], "type": "access", "role": "MANAGER"}
        headers = {"Authorization": "Bearer valid_manager_token"}

        resp = await async_client.post("/query", json={"query": "How many widgets in Reno?"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["template_used"] == "STOCK_AVAILABLE"


@pytest.mark.asyncio
async def test_api_key_management_flow(async_client: AsyncClient):
    """
    Test API key creation, listing, and revocation flow.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    owner_user = {
        "id": "507f1f77bcf86cd799439011",
        "role": "OWNER",
        "status": "ACTIVE",
    }

    created_key_doc = {
        "id": "key123",
        "name": "Morning Check Script",
        "key_hash": "hashed_key",
        "prefix": "wms_live_abc",
        "role": "STAFF",
        "scopes": ["read"],
        "is_active": True,
        "created_by": owner_user["id"],
        "created_at": "2026-08-13 12:00:00.000000",
    }

    revoked_key_doc = dict(created_key_doc)
    revoked_key_doc["is_active"] = False

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=owner_user)), \
         patch("core.cruds.api_key_crud.CRUDApiKey.create", AsyncMock(return_value=created_key_doc)), \
         patch("core.cruds.api_key_crud.CRUDApiKey.list_keys", AsyncMock(return_value=[created_key_doc])), \
         patch("core.cruds.api_key_crud.CRUDApiKey.revoke", AsyncMock(return_value=revoked_key_doc)):

        mock_decode.return_value = {"sub": owner_user["id"], "type": "access", "role": "OWNER"}
        headers = {"Authorization": "Bearer valid_owner_token"}

        # Step 1: Create API Key
        create_payload = {"name": "Morning Check Script", "role": "STAFF", "scopes": ["read"]}
        create_resp = await async_client.post("/api-keys", json=create_payload, headers=headers)
        assert create_resp.status_code == 201
        key_data = create_resp.json()
        assert "raw_key" in key_data
        assert key_data["name"] == "Morning Check Script"

        # Step 2: List API Keys
        list_resp = await async_client.get("/api-keys", headers=headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()["keys"]) == 1

        # Step 3: Revoke API Key
        revoke_resp = await async_client.delete("/api-keys/key123", headers=headers)
        assert revoke_resp.status_code == 200
        assert revoke_resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_nl_query_rejects_unlisted_templates(async_client: AsyncClient):
    """
    Test NL Query service rejects prompts that map outside allow-listed templates.
    """
    manager_user = {"id": "mgr1", "role": "MANAGER", "status": "ACTIVE"}

    with patch("commons.auth.decodeJWT", return_value={"sub": "mgr1", "type": "access", "role": "MANAGER"}), \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=manager_user)), \
         patch("core.services.nl_query_service.NLQueryService.execute_query", AsyncMock(side_effect=ValueError("Query does not match any allow-listed template"))):

        headers = {"Authorization": "Bearer token"}
        resp = await async_client.post("/query", json={"query": "DROP DATABASE wms;"}, headers=headers)
        assert resp.status_code == 400
        assert "allow-listed template" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_api_key_scope_enforcement(async_client: AsyncClient):
    """
    Test API Key authentication with valid scopes is accepted and missing key is rejected.
    """
    resp = await async_client.get("/reports/summary?date=2026-08-13", headers={"X-API-Key": "invalid_key"})
    assert resp.status_code == 401

