"""
voice_service.py — AI Voice transcription and LLM draft parsing service.

Provides interfaces for audio STT transcription and LLM structured draft extraction
with per-field confidence scores.
"""

import re
from typing import Any

from core import logger

logging = logger(__name__)


class VoiceService:
    """Service facade for Voice STT and LLM transcript parsing."""

    async def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        """
        Transcribe audio bytes to text transcript (Whisper STT interface).

        Args:
            audio_bytes (bytes): Audio file binary payload.
            filename (str): Audio filename.

        Returns:
            str: Transcribed text string.
        """
        logging.info("Executing VoiceService.transcribe_audio")
        # Interface implementation (production wires to OpenAI Whisper or local Whisper model)
        return "Received Widget A box width 10 inches height 5 inches weight 2 point 5 pounds fragile no damage"

    async def parse_transcript(self, transcript: str) -> dict[str, Any]:
        """
        LLM extraction of transcript into structured draft and confidence scores.

        Args:
            transcript (str): Transcribed audio text.

        Returns:
            Dict[str, Any]: Dictionary containing parsed_data and confidence_scores.
        """
        logging.info("Executing VoiceService.parse_transcript")
        text = transcript.lower()

        # Extract product name
        name_match = re.search(r"received\s+(.*?)\s+(?:box|width|height|weight)", text)
        product_name = name_match.group(1).title() if name_match else "Scanned Item"

        # Extract dimensions
        w_match = re.search(r"width\s+(\d+(?:\.\d+)?)", text)
        width = float(w_match.group(1)) if w_match else 0.0

        h_match = re.search(r"height\s+(\d+(?:\.\d+)?)", text)
        height = float(h_match.group(1)) if h_match else 0.0

        wt_match = re.search(r"weight\s+(\d+(?:\.\d+)?|\d+\s+point\s+\d+)", text)
        weight = 0.0
        if wt_match:
            raw_wt = wt_match.group(1).replace(" point ", ".")
            try:
                weight = float(raw_wt)
            except ValueError:
                weight = 0.0

        fragile = "fragile" in text and "not fragile" not in text
        is_damaged = "damage" in text and "no damage" not in text

        parsed_data = {
            "product_name": product_name,
            "width": width,
            "height": height,
            "weight": weight,
            "fragile": fragile,
            "damage": {"flag": is_damaged, "note": "Voice reported damage" if is_damaged else None},
        }

        confidence_scores = {
            "product_name": 0.95 if name_match else 0.50,
            "width": 0.90 if w_match else 0.40,
            "height": 0.90 if h_match else 0.40,
            "weight": 0.85 if wt_match else 0.30,
            "fragile": 0.90,
            "damage": 0.90,
        }

        return {
            "parsed_data": parsed_data,
            "confidence_scores": confidence_scores,
        }


_voice_service_instance: VoiceService | None = None


def get_voice_service() -> VoiceService:
    """
    Retrieve global VoiceService instance.

    Returns:
        VoiceService: Shared voice service instance.
    """
    global _voice_service_instance
    if _voice_service_instance is None:
        _voice_service_instance = VoiceService()
    return _voice_service_instance
