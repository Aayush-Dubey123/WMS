"""
user_responses.py — Pydantic schemas for outgoing user API responses.

These models shape exactly what gets serialised into the JSON response.
Sensitive fields (like hashed_password) are deliberately excluded here.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """
    Response model returned when the API sends user profile data.

    This model is used by endpoints such as register and get current user.
    Sensitive values such as hashed_password are intentionally excluded.
    """

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    mobile_number: str | None
    role: str
    status: str
    created_at: datetime


class LoginResponse(BaseModel):
    """
    Response model returned after a successful login.

    The API returns a JWT access token and a nested user profile object.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Simple response model used when only a text message is returned."""

    message: str
