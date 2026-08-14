"""
chatbot_router.py — WMS Chatbot integration router.

Provides natural language interface to WMS operations:
- Staff FAQ (SOP-grounded)
- Manager stock lookups via NL query templates
- Audit log lookups
- Voice logging confirmation dialogues

Reuses commons/auth.py for JWT validation and role-based access control.
All tool calls flow through existing controllers/CRUDs—no direct DB access.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from commons.auth import require_roles, decodeJWT
from core import logger
from core.controllers.chatbot_controller import ChatbotController

logging = logger(__name__)

chatbot_router = APIRouter(prefix="/chat", tags=["Chatbot — NL Assistant"])


class ChatRequest(BaseModel):
    """Request body for chatbot endpoint."""
    conversation_id: str
    user_input: str


class ChatResponse(BaseModel):
    """Response from chatbot."""
    response: str
    conversation_id: str


@chatbot_router.post(
    "/message",
    status_code=status.HTTP_200_OK,
    response_model=ChatResponse,
)
async def chat_message(
    request: ChatRequest,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER", "STAFF"])),
):
    """
    Send a message to the WMS chatbot and get a response.

    The chatbot respects role-based access:
    - STAFF: FAQ, order tracking, arrival logging
    - MANAGER: Stock lookups, approvals, team queries
    - OWNER: Full system queries, audit access

    Args:
        request: Chat message request
        current_user: Authenticated user (any role)

    Returns:
        ChatResponse with chatbot reply

    Raises:
        HTTPException: On auth/validation/processing errors
    """
    try:
        logging.info(
            f"Chat message from {current_user.get('email')} (role={current_user.get('role')})"
        )

        controller = ChatbotController()
        reply = await controller.run_turn(
            conversation_id=request.conversation_id,
            user_input=request.user_input,
            current_user=current_user,
        )

        return ChatResponse(
            response=reply,
            conversation_id=request.conversation_id,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logging.error(f"Error in POST /chat/message: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@chatbot_router.get(
    "/history/{conversation_id}",
    status_code=status.HTTP_200_OK,
)
async def get_chat_history(
    conversation_id: str,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER", "STAFF"])),
):
    """
    Retrieve chat history for a conversation.

    Args:
        conversation_id: Conversation identifier
        current_user: Authenticated user

    Returns:
        Chat history list
    """
    try:
        controller = ChatbotController()
        history = await controller.get_history(conversation_id, current_user)
        return {"conversation_id": conversation_id, "history": history}
    except HTTPException:
        raise
    except Exception as exc:
        logging.error(f"Error in GET /chat/history: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
