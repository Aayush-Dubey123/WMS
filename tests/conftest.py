"""
conftest.py — Pytest configuration and shared test fixtures.

Provides async httpx client fixture bound to the FastAPI application.
Initializes test environment settings.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from core.apis.api import app


@pytest_asyncio.fixture
async def async_client():
    """
    Provide an async HTTP test client for API endpoint testing.

    Yields:
        AsyncClient: Configured httpx AsyncClient instance bound to app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
