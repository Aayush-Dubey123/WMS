"""
test_health.py — Health check endpoint unit tests.

Tests GET /health and root ping endpoints for correct status code and response schema.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_ping(async_client: AsyncClient):
    """
    Test root GET / endpoint response.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """
    Test GET /health endpoint response.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    response = await async_client.get("/health")
    # Status code is 200 (connected) or 503 (disconnected if no local mongo running during unit test)
    assert response.status_code in (200, 503)
    data = response.json()
    if response.status_code == 200:
        assert data["status"] == "ok"
        assert "database" in data
        assert "timestamp" in data
