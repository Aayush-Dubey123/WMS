"""
voice_request.py — Request schemas for voice pipeline endpoints.

Defines Pydantic models for transcript parsing and draft confirmation.
"""

from pydantic import BaseModel, Field


class VoiceParseRequest(BaseModel):
    """Payload for LLM transcript parsing."""

    ticket_id: str = Field(..., description="Target ticket ID")
    transcript: str = Field(..., description="Transcribed voice audio text string")


class VoiceConfirmRequest(BaseModel):
    """Payload for confirming a voice draft."""

    barcode: str = Field(..., description="Confirmed product barcode / UPC code")
    override_weight: float = Field(..., gt=0, description="Manual confirmed weight (lbs)")
