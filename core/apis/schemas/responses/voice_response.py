"""
voice_response.py â€” Response schemas for voice pipeline endpoints.

Defines response models for transcription and draft extraction.
"""

from typing import Any

from pydantic import BaseModel, Field

from core.models.wms_models import DraftStatus


class TranscribeResponse(BaseModel):
    """Response payload for audio transcription."""

    transcript: str = Field(..., description="Transcribed audio text string")


class VoiceDraftResponse(BaseModel):
    """Response payload for voice parsed draft."""

    id: str = Field(..., description="Voice draft ID string")
    ticket_id: str = Field(..., description="Target ticket ID")
    transcript: str = Field(..., description="Audio transcript string")
    parsed_data: dict[str, Any] = Field(..., description="Extracted draft item fields")
    confidence_scores: dict[str, float] = Field(..., description="Per-field AI confidence scores")
    status: DraftStatus = Field(..., description="Draft status (DRAFT, CONFIRMED, DISCARDED)")
    created_at: str = Field(..., description="UTC creation timestamp string")

