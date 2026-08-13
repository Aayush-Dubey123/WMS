"""
auth_request.py — Request schemas for authentication endpoints.

Defines Pydantic models for user login and token refresh requests.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request body payload for POST /auth/login."""

    email: EmailStr = Field(..., description="User account email address", example="owner@whitfield.com")
    password: str = Field(..., description="Plaintext password", example="SecurePass123!")


class RefreshTokenRequest(BaseModel):
    """Request body payload for POST /auth/refresh."""

    refresh_token: str = Field(..., description="Valid JWT refresh token string")
