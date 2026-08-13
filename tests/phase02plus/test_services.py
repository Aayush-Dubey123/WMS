"""
test_services.py â€” Direct unit tests for core services to ensure high code coverage.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from pymongo.errors import DuplicateKeyError

from core.services.wms_service import AuditService, get_audit_service
from core.services.wms_service import IdempotencyService, get_idempotency_service
from core.services.integration_service import ExportService, get_export_service
from core.services.integration_service import LocalStorageService, get_storage_service
from core.services.ai_service import NLQueryService, get_nl_query_service
from core.services.ai_service import VisionService, get_vision_service
from core.services.ai_service import VoiceService, get_voice_service


def test_export_service_csv():
    service = ExportService()
    empty = service.generate_csv([])
    assert empty == b""

    records = [{"item": "Widget A", "count": 10}]
    csv_bytes = service.generate_csv(records)
    assert b"Widget A" in csv_bytes
    assert get_export_service() is not None


def test_export_service_xlsx():
    service = ExportService()
    empty = service.generate_xlsx([], title="EmptySheet")
    assert isinstance(empty, bytes)

    records = [{"item": "Widget A", "data": {"a": 1}}]
    xlsx_bytes = service.generate_xlsx(records, title="DataSheet")
    assert isinstance(xlsx_bytes, bytes)


@pytest.mark.asyncio
async def test_storage_service():
    service = LocalStorageService()
    invalid_file = UploadFile(filename="test.pdf", file=None)
    with pytest.raises(HTTPException) as exc:
        await service.save_image(invalid_file)
    assert exc.value.status_code == 400

    valid_file = UploadFile(filename="test.png", file=MagicMock(read=AsyncMock(return_value=b"fake_png")))
    with patch("aiofiles.open", MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(write=AsyncMock())), __aexit__=AsyncMock()))):
        url = await service.save_image(valid_file)
        assert url.startswith("/uploads/")

    assert get_storage_service() is not None


@pytest.mark.asyncio
async def test_vision_service():
    service = VisionService()
    res_invalid = await service.measure_package(b"invalid_image")
    assert res_invalid["marker_found"] is False
    assert res_invalid["weight"] == 0.0

    assert get_vision_service() is not None


@pytest.mark.asyncio
async def test_nl_query_service():
    service = NLQueryService()

    with patch("core.services.ai_service.MongoDatabase") as mock_db:
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[{"_id": "Widget A", "count": 5}])
        mock_db.return_value.items.aggregate.return_value = mock_cursor

        res_avail = await service.execute_query("How many items available?", user_role="STAFF")
        assert res_avail["template_used"] == "STOCK_AVAILABLE"

        res_dam = await service.execute_query("Show broken stock", user_role="MANAGER", warehouse_id="wh1")
        assert res_dam["template_used"] == "STOCK_DAMAGED"

        res_res = await service.execute_query("Show held stock", user_role="OWNER")
        assert res_res["template_used"] == "STOCK_RESERVED"

    assert get_nl_query_service() is not None


@pytest.mark.asyncio
async def test_idempotency_service():
    service = IdempotencyService()

    with patch("core.services.wms_service.MongoDatabase") as mock_db:
        mock_db.return_value.idempotency_keys.insert_one = AsyncMock(return_value=True)
        res = await service.lock_key("key1", "/endpoint", "actor1")
        assert res is True

        mock_db.return_value.idempotency_keys.insert_one = AsyncMock(side_effect=DuplicateKeyError("Duplicate"))
        with pytest.raises(HTTPException) as exc:
            await service.lock_key("key1", "/endpoint", "actor1")
        assert exc.value.status_code == 409

    assert get_idempotency_service() is not None


@pytest.mark.asyncio
async def test_audit_service():
    service = AuditService()
    with patch("core.services.wms_service.CRUDAuditLog.create", AsyncMock(return_value={"id": "audit1"})):
        await service.log_mutation(actor={"id": "usr1"}, action="TEST", collection="test", doc_id="1")

    assert get_audit_service() is not None


@pytest.mark.asyncio
async def test_voice_service():
    service = VoiceService()
    transcript = await service.transcribe_audio(b"audio", "file.wav")
    assert isinstance(transcript, str)

    parsed = await service.parse_transcript("Widget A width 10 height 5")
    assert parsed["parsed_data"]["product_name"] == "Scanned Item"

    assert get_voice_service() is not None

