"""
test_ticket_generator.py — Unit tests for atomic ticket generator utility.

Tests sequence incrementing and ticket string formatting.
"""

from unittest.mock import AsyncMock, patch

import pytest

from core.utils.ticket_generator import TicketGenerator


@pytest.mark.asyncio
async def test_ticket_generator_format():
    """
    Test TicketGenerator generates correctly formatted ticket ID string.

    Verifies ticket ID pattern {WH}-{YYYYMMDD}-{SEQ:03d}.
    """
    generator = TicketGenerator()
    fake_counter_doc = {"seq": 14}

    with patch("core.utils.ticket_generator.MongoDatabase") as mock_db:
        mock_db_instance = mock_db.return_value
        mock_db_instance.counters.find_one_and_update = AsyncMock(
            return_value=fake_counter_doc
        )

        ticket_id = await generator.generate_ticket_id("RNO")
        assert ticket_id.startswith("RNO-")
        assert ticket_id.endswith("-014")
        assert len(ticket_id.split("-")) == 3
