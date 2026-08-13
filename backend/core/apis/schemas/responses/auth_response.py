"""
auth_response.py — Response schemas for authentication endpoints.

Defines TokenResponse and UserMeResponse models.
"""


from pydantic import BaseModel, EmailStr, Field

from core.models.user_model import ExperienceTier, FunctionRole, UserRole, UserStatus


class TokenResponse(BaseModel):
    """Response model for login and token refresh requests."""

    access_token: str = Field(..., description="JWT access token string")
    refresh_token: str = Field(..., description="JWT refresh token string")
    token_type: str = Field(default="bearer", description="Token authorization header type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class UserMeResponse(BaseModel):
    """Response model for GET /auth/me user profile request."""

    id: str = Field(..., description="User unique ID string")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User full legal name")
    role: UserRole = Field(..., description="RBAC role string")
    warehouse_id: str | None = Field(default=None, description="Assigned warehouse ID")
    experience_tier: ExperienceTier | None = Field(default=None, description="Experience tier for staff")
    function_roles: list[FunctionRole] = Field(default_factory=list, description="List of operational function roles")
    status: UserStatus = Field(..., description="Account lifecycle status")
