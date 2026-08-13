"""
voice_controller.py — Controller for voice transcription, LLM parsing, and draft confirmation.

Handles audio transcription, LLM transcript extraction, saving draft documents, and
confirming drafts by calling the identical Phase 2 TicketController item-logging pipeline.
"""

from fastapi import HTTPException, status

from core import logger
from core.controllers.ticket_controller import TicketController
from core.cruds.voice_draft_crud import CRUDVoiceDraft
from core.models.voice_draft_model import DraftStatus
from core.services.voice_service import get_voice_service

logging = logger(__name__)


class VoiceController:
    """Controller managing voice audio processing and draft item confirmations."""

    def __init__(self):
        """Initialize VoiceController with VoiceService and CRUDVoiceDraft."""
        self._voice_service = get_voice_service()
        self._draft_crud = CRUDVoiceDraft()

    async def transcribe(self, audio_bytes: bytes, filename: str, current_user: dict) -> dict:
        """
        Transcribe audio file payload to text transcript.

        Args:
            audio_bytes (bytes): Binary audio content.
            filename (str): Audio filename.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Transcript payload dictionary.
        """
        try:
            logging.info("Executing VoiceController.transcribe")
            transcript = await self._voice_service.transcribe_audio(audio_bytes=audio_bytes, filename=filename)
            return {"transcript": transcript}
        except Exception as error:
            logging.error(f"Error in VoiceController.transcribe: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def parse_transcript(self, ticket_id: str, transcript: str, current_user: dict) -> dict:
        """
        Parse text transcript into structured draft item using LLM and save as DRAFT.

        Args:
            ticket_id (str): Target arrival ticket ID string.
            transcript (str): Audio transcript string.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Saved voice draft document payload.
        """
        try:
            logging.info(f"Executing VoiceController.parse_transcript for ticket: {ticket_id}")
            parsed_res = await self._voice_service.parse_transcript(transcript=transcript)

            wh_id = current_user.get("warehouse_id", "wh_default")

            draft_payload = {
                "user_id": current_user["id"],
                "warehouse_id": wh_id,
                "ticket_id": ticket_id,
                "transcript": transcript,
                "parsed_data": parsed_res["parsed_data"],
                "confidence_scores": parsed_res["confidence_scores"],
                "status": DraftStatus.DRAFT.value,
            }

            created_draft = await self._draft_crud.create(draft_payload)
            logging.info(f"Voice draft saved successfully! Draft ID: {created_draft['id']}")
            return created_draft
        except Exception as error:
            logging.error(f"Error in VoiceController.parse_transcript: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def confirm_draft(
        self,
        draft_id: str,
        barcode: str,
        override_weight: float,
        current_user: dict,
    ) -> dict:
        """
        Confirm voice draft by writing through the EXACT SAME Phase 2 item logging service pipeline.

        No AI shortcut or DB bypass: calls TicketController.log_item_scan directly!

        Args:
            draft_id (str): Voice draft ID string.
            barcode (str): Confirmed product barcode.
            override_weight (float): Confirmed manual item weight.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Created item unit record payload from Phase 2 pipeline.

        Raises:
            HTTPException 404: Voice draft not found.
            HTTPException 400: Draft already processed or discarded.
        """
        try:
            logging.info(f"Executing VoiceController.confirm_draft for draft: {draft_id}")
            draft = await self._draft_crud.get_by_id(id=draft_id)
            if not draft:
                logging.warning(f"Voice draft confirm failed: draft {draft_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Voice draft not found",
                )

            if draft.get("status") != DraftStatus.DRAFT.value:
                logging.warning(f"Voice draft confirm rejected: status is {draft.get('status')}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Voice draft status is '{draft.get('status')}', expected DRAFT",
                )

            parsed = draft.get("parsed_data", {})

            # Prepare item payload for Phase 2 item logging service
            item_scan_data = {
                "barcode": barcode.strip(),
                "product_name": parsed.get("product_name", "Scanned Item"),
                "width": float(parsed.get("width", 0.0)),
                "height": float(parsed.get("height", 0.0)),
                "weight": float(override_weight),
                "image_url": None,
                "damage": parsed.get("damage", {"flag": False, "note": None}),
            }

            # Invoke identical Phase 2 logging service controller pipeline
            created_item = await TicketController().log_item_scan(
                ticket_id=draft["ticket_id"],
                item_data=item_scan_data,
                current_user=current_user,
            )

            # Update draft status to CONFIRMED
            await self._draft_crud.update(id=draft_id, update_in={"status": DraftStatus.CONFIRMED.value})

            logging.info(f"Voice draft confirmed and logged through Phase 2 pipeline! Draft ID: {draft_id}")
            return created_item
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in VoiceController.confirm_draft: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
