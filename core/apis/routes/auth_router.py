"""
auth_router.py — Authentication endpoint routes.

Exposes endpoints for user login, token refresh, and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from commons.auth import get_current_user
from core import logger
from core.apis.schemas.requests.auth_request import LoginRequest, RefreshTokenRequest
from core.apis.schemas.responses.auth_response import TokenResponse, UserMeResponse
from core.controllers.auth_controller import AuthController

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
logging = logger(__name__)


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def login(request: LoginRequest):
    """
    Authenticate user credentials and issue access and refresh tokens.

    Verifies email address and password against stored password hash.

    Args:
        request (LoginRequest): Login payload containing email and password.

    Returns:
        TokenResponse: Access and refresh tokens with expiration.

    Raises:
        HTTPException 401: Invalid credentials.
        HTTPException 403: User account inactive.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /auth/login endpoint")
        response = await AuthController().login(login_data=request.model_dump())
        return TokenResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /auth/login endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /auth/login endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@auth_router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh JWT access token.

    Validates refresh token and issues a new access/refresh token pair.

    Args:
        request (RefreshTokenRequest): Request payload containing refresh token string.

    Returns:
        TokenResponse: Fresh access and refresh tokens.

    Raises:
        HTTPException 401: Expired or invalid refresh token.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /auth/refresh endpoint")
        response = await AuthController().refresh_token(refresh_token_str=request.refresh_token)
        return TokenResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /auth/refresh endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /auth/refresh endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@auth_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserMeResponse,
)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Retrieve authenticated user profile.

    Returns profile information, role, assigned warehouse, and tier for active user.

    Args:
        current_user (dict): Authenticated user dependency.

    Returns:
        UserMeResponse: Authenticated user details.

    Raises:
        HTTPException 401: Unauthorized access.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling GET /auth/me endpoint")
        response = await AuthController().get_me(current_user=current_user)
        return UserMeResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /auth/me endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /auth/me endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
