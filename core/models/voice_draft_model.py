"""
voice_draft_model.py — Voice draft persistence document schema.

Defines VoiceDraft document schema stored in MongoDB voice_drafts collection.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from pytz import timezone


class DraftStatus(str, Enum):
    """Voice draft lifecycle status enum."""
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    DISCARDED = "DISCARDED"


class VoiceDraft(BaseModel):
    """
    Voice draft database document schema.

    Holds unconfirmed AI extracted item logging drafts before rookie/staff confirmation.
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    user_id: str = Field(..., description="ID of staff user recording voice")
    warehouse_id: str = Field(..., description="Warehouse facility ID")
    ticket_id: str = Field(..., description="Target ticket ID string")
    transcript: str = Field(..., description="Transcribed audio text")
    parsed_data: dict[str, Any] = Field(
        ..., description="Extracted fields {product_name, width, height, weight, fragile, damage}"
    )
    confidence_scores: dict[str, float] = Field(
        default_factory=dict, description="Per-field AI confidence scores (0.0 to 1.0)"
    )
    status: DraftStatus = Field(
        default=DraftStatus.DRAFT, description="Draft lifecycle status"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
