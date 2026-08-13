"""
auth_controller.py — Controller for authentication operations.

Handles user authentication, password verification, JWT issuance, and token refresh.
"""

from fastapi import HTTPException, status

from commons.auth import (
    create_access_token,
    create_refresh_token,
    decodeJWT,
    verify_password,
)
from core import logger
from core.config.settings import settings
from core.cruds.user_crud import CRUDUser

logging = logger(__name__)


class AuthController:
    """Controller managing authentication workflows."""

    def __init__(self):
        """Initialize AuthController with CRUDUser instance."""
        self._user_crud = CRUDUser()

    async def login(self, login_data: dict) -> dict:
        """
        Authenticate user credentials and issue JWT tokens.

        Args:
            login_data (dict): Login request containing email and password.

        Returns:
            dict: Token payload dictionary containing access_token, refresh_token, and expiration.

        Raises:
            HTTPException 401: Invalid email or password credentials.
            HTTPException 403: User account is not ACTIVE.
            HTTPException 500: Internal server error.
        """
        try:
            logging.info("Executing AuthController.login")
            email = login_data.get("email", "").lower().strip()
            password = login_data.get("password", "")

            user = await self._user_crud.get_by_email(email=email)
            if not user:
                logging.warning(f"Login failed: user email not found ({email})")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            if not verify_password(password, user.get("hashed_password", "")):
                logging.warning(f"Login failed: invalid password for user ({email})")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            if user.get("status") != "ACTIVE":
                logging.warning(f"Login blocked: user account is inactive ({email})")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive or suspended",
                )

            token_data = {
                "sub": str(user["id"]),
                "email": user["email"],
                "role": user["role"],
                "warehouse_id": user.get("warehouse_id"),
                "experience_tier": user.get("experience_tier"),
            }

            access_token = create_access_token(data=token_data)
            refresh_token = create_refresh_token(data=token_data)

            logging.info(f"User login successful: {email} ({user['role']})")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AuthController.login: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def refresh_token(self, refresh_token_str: str) -> dict:
        """
        Issue a new JWT access token using a valid refresh token.

        Args:
            refresh_token_str (str): JWT refresh token string.

        Returns:
            dict: New token payload dictionary.

        Raises:
            HTTPException 401: Invalid or expired refresh token.
            HTTPException 403: User account is inactive.
        """
        try:
            logging.info("Executing AuthController.refresh_token")
            payload = decodeJWT(refresh_token_str)
            if not payload or payload.get("type") != "refresh":
                logging.warning("Refresh token check failed: invalid payload or token type")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token",
                )

            user_id = payload.get("sub")
            user = await self._user_crud.get_by_id(id=user_id)
            if not user or user.get("status") != "ACTIVE":
                logging.warning(f"Refresh token blocked: invalid or inactive user ({user_id})")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is invalid or inactive",
                )

            token_data = {
                "sub": str(user["id"]),
                "email": user["email"],
                "role": user["role"],
                "warehouse_id": user.get("warehouse_id"),
                "experience_tier": user.get("experience_tier"),
            }

            new_access_token = create_access_token(data=token_data)
            new_refresh_token = create_refresh_token(data=token_data)

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AuthController.refresh_token: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_me(self, current_user: dict) -> dict:
        """
        Format authenticated user profile payload.

        Args:
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: User profile response dictionary.
        """
        logging.info(f"Executing AuthController.get_me for user: {current_user.get('email')}")
        return {
            "id": str(current_user["id"]),
            "email": current_user["email"],
            "full_name": current_user["full_name"],
            "role": current_user["role"],
            "warehouse_id": current_user.get("warehouse_id"),
            "experience_tier": current_user.get("experience_tier"),
            "function_roles": current_user.get("function_roles", []),
            "status": current_user["status"],
        }
