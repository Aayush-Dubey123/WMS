"""
user_response.py — Response schemas for user management endpoints.

Defines UserResponse and UserListResponse models.
"""


from pydantic import BaseModel, EmailStr, Field

from core.models.user_model import ExperienceTier, FunctionRole, UserRole, UserStatus


class UserResponse(BaseModel):
    """Response payload representing user account details."""

    id: str = Field(..., description="User unique ID string")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="System RBAC role")
    warehouse_id: str | None = Field(default=None, description="Assigned warehouse ID")
    experience_tier: ExperienceTier | None = Field(default=None, description="Experience tier for staff")
    function_roles: list[FunctionRole] = Field(default_factory=list, description="Assigned operational function roles")
    status: UserStatus = Field(..., description="User active status")
    created_at: str = Field(..., description="UTC creation timestamp string")


class UserListResponse(BaseModel):
    """Response payload wrapper for listing user accounts."""

    users: list[UserResponse] = Field(..., description="List of user account objects")
    total: int = Field(..., description="Total matching user record count")
