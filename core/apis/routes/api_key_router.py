"""
api_key_router.py — API Key administration routes.

Exposes endpoints for POST /api-keys, GET /api-keys, and DELETE /api-keys/{id}.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from commons.auth import require_roles
from core import logger
from core.apis.schemas.requests.api_key_request import ApiKeyCreateRequest
from core.apis.schemas.responses.api_key_response import (
    ApiKeyCreatedResponse,
    ApiKeyItemResponse,
    ApiKeyListResponse,
)
from core.controllers.api_key_controller import ApiKeyController

api_key_router = APIRouter(prefix="/api-keys", tags=["API Key Scripting Integration"])
logging = logger(__name__)


@api_key_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiKeyCreatedResponse,
)
async def create_api_key(
    request: ApiKeyCreateRequest,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Generate a new scoped API Key for external script integration.

    Returns the raw secret key ONCE upon creation.

    Args:
        request (ApiKeyCreateRequest): Key creation parameters.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        ApiKeyCreatedResponse: Created key object with raw_key.
    """
    try:
        logging.info("Calling POST /api-keys endpoint")
        response = await ApiKeyController().create_key(
            key_data=request.model_dump(),
            current_user=current_user,
        )
        return ApiKeyCreatedResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /api-keys endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /api-keys endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@api_key_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiKeyListResponse,
)
async def list_api_keys(
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    List active and revoked API keys created by current user.

    Args:
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        ApiKeyListResponse: List of API key items (without raw secrets).
    """
    try:
        logging.info("Calling GET /api-keys endpoint")
        keys = await ApiKeyController().list_keys(current_user=current_user)
        return ApiKeyListResponse(keys=[ApiKeyItemResponse(**k) for k in keys])
    except HTTPException as httperror:
        logging.error(f"Error in GET /api-keys endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /api-keys endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@api_key_router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiKeyItemResponse,
)
async def revoke_api_key(
    id: str,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Revoke an API key.

    Args:
        id (str): API key ID.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        ApiKeyItemResponse: Revoked key record.
    """
    try:
        logging.info(f"Calling DELETE /api-keys/{id} endpoint")
        revoked = await ApiKeyController().revoke_key(key_id=id, current_user=current_user)
        return ApiKeyItemResponse(**revoked)
    except HTTPException as httperror:
        logging.error(f"Error in DELETE /api-keys/{id} endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in DELETE /api-keys/{id} endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
