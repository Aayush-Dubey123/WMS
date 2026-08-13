"""
test_reports.py — Unit and integration tests for Phase 4 Reporting and Exports.

Tests executive summary metrics, detail feeds, stock totals aggregation, and CSV/XLSX file downloads.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_reports_summary(async_client: AsyncClient):
    """
    Test GET /reports/summary endpoint returns executive dashboard metrics.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    owner_user = {
        "id": "507f1f77bcf86cd799439011",
        "email": "owner@whitfield.com",
        "role": "OWNER",
        "status": "ACTIVE",
    }

    fake_summary = {
        "date": "2026-08-13",
        "todays_tickets": 15,
        "todays_sold": 42,
        "arrived_missed": 3,
        "per_warehouse": [
            {
                "warehouse_id": "607f1f77bcf86cd799439022",
                "todays_tickets": 15,
                "todays_sold": 42,
                "arrived_missed": 3,
            }
        ],
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=owner_user)), \
         patch("core.controllers.report_controller.ReportController.get_summary", AsyncMock(return_value=fake_summary)):

        mock_decode.return_value = {"sub": owner_user["id"], "type": "access", "role": "OWNER"}
        headers = {"Authorization": "Bearer valid_owner_token"}

        response = await async_client.get("/reports/summary?date=2026-08-13", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["todays_tickets"] == 15
        assert data["todays_sold"] == 42
        assert data["arrived_missed"] == 3


@pytest.mark.asyncio
async def test_get_reports_stock(async_client: AsyncClient):
    """
    Test GET /reports/stock endpoint returns aggregated product stock totals.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    manager_user = {
        "id": "707f1f77bcf86cd799439033",
        "email": "manager.rno@whitfield.com",
        "role": "MANAGER",
        "warehouse_id": "607f1f77bcf86cd799439022",
        "status": "ACTIVE",
    }

    fake_stock_payload = {
        "stock": [
            {
                "barcode": "012345678905",
                "product_name": "Widget A",
                "warehouse_id": "607f1f77bcf86cd799439022",
                "on_hand": 100,
                "available": 80,
                "reserved": 20,
                "damaged": 5,
            }
        ],
        "total_on_hand": 100,
        "total_available": 80,
        "total_reserved": 20,
        "total_damaged": 5,
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=manager_user)), \
         patch("core.controllers.report_controller.ReportController.get_stock_totals", AsyncMock(return_value=fake_stock_payload)):

        mock_decode.return_value = {"sub": manager_user["id"], "type": "access", "role": "MANAGER"}
        headers = {"Authorization": "Bearer valid_manager_token"}

        response = await async_client.get("/reports/stock", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_on_hand"] == 100
        assert data["stock"][0]["barcode"] == "012345678905"


@pytest.mark.asyncio
async def test_export_report_csv(async_client: AsyncClient):
    """
    Test GET /reports/export?report_type=stock&format=csv returns CSV file download stream.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    owner_user = {
        "id": "507f1f77bcf86cd799439011",
        "role": "OWNER",
        "status": "ACTIVE",
    }

    fake_csv_bytes = b"barcode,product_name,on_hand\n012345678905,Widget A,100\n"

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=owner_user)), \
         patch("core.controllers.report_controller.ReportController.export_report", AsyncMock(return_value=(fake_csv_bytes, "text/csv", "stock_report.csv"))):

        mock_decode.return_value = {"sub": owner_user["id"], "type": "access", "role": "OWNER"}
        headers = {"Authorization": "Bearer valid_owner_token"}

        response = await async_client.get("/reports/export?report_type=stock&format=csv", headers=headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8" or response.headers["content-type"] == "text/csv"
        assert "attachment" in response.headers["content-disposition"]
        assert b"Widget A" in response.content
