"""
voice_router.py — AI Voice processing endpoint routes.

Exposes endpoints for POST /voice/transcribe, POST /voice/parse, and POST /voice/drafts/{id}/confirm.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from commons.auth import get_current_user
from core import logger
from core.apis.schemas.requests.voice_request import (
    VoiceConfirmRequest,
    VoiceParseRequest,
)
from core.apis.schemas.responses.item_response import ItemResponse
from core.apis.schemas.responses.voice_response import (
    TranscribeResponse,
    VoiceDraftResponse,
)
from core.controllers.voice_controller import VoiceController

voice_router = APIRouter(prefix="/voice", tags=["Voice Pipeline"])
logging = logger(__name__)


@voice_router.post(
    "/transcribe",
    status_code=status.HTTP_200_OK,
    response_model=TranscribeResponse,
)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Transcribe uploaded voice audio to text string.

    Args:
        file (UploadFile): Audio file binary upload.
        current_user (dict): Authenticated user dependency.

    Returns:
        TranscribeResponse: Audio transcript payload.
    """
    try:
        logging.info("Calling POST /voice/transcribe endpoint")
        audio_bytes = await file.read()
        response = await VoiceController().transcribe(
            audio_bytes=audio_bytes,
            filename=file.filename,
            current_user=current_user,
        )
        return TranscribeResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /voice/transcribe endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /voice/transcribe endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@voice_router.post(
    "/parse",
    status_code=status.HTTP_201_CREATED,
    response_model=VoiceDraftResponse,
)
async def parse_transcript(
    request: VoiceParseRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Parse text transcript into structured unconfirmed draft item using LLM.

    Args:
        request (VoiceParseRequest): Parse parameters.
        current_user (dict): Authenticated user dependency.

    Returns:
        VoiceDraftResponse: Created voice draft object.
    """
    try:
        logging.info("Calling POST /voice/parse endpoint")
        response = await VoiceController().parse_transcript(
            ticket_id=request.ticket_id,
            transcript=request.transcript,
            current_user=current_user,
        )
        return VoiceDraftResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /voice/parse endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /voice/parse endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@voice_router.post(
    "/drafts/{id}/confirm",
    status_code=status.HTTP_201_CREATED,
    response_model=ItemResponse,
)
async def confirm_draft(
    id: str,
    request: VoiceConfirmRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Confirm voice draft and write through identical Phase 2 item logging service pipeline.

    Args:
        id (str): Voice draft ID string.
        request (VoiceConfirmRequest): Confirmed barcode and manual weight override.
        current_user (dict): Authenticated user dependency.

    Returns:
        ItemResponse: Created item unit record payload.
    """
    try:
        logging.info(f"Calling POST /voice/drafts/{id}/confirm endpoint")
        response = await VoiceController().confirm_draft(
            draft_id=id,
            barcode=request.barcode,
            override_weight=request.override_weight,
            current_user=current_user,
        )
        return ItemResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /voice/drafts/{id}/confirm endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /voice/drafts/{id}/confirm endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
