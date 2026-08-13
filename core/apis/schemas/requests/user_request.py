"""
user_request.py — Request schemas for user management endpoints.

Defines Pydantic models for Manager creation, Staff creation, and Staff updates.
"""


from pydantic import BaseModel, EmailStr, Field

from core.models.user_model import ExperienceTier, FunctionRole


class ManagerCreateRequest(BaseModel):
    """Payload for Owner creating a Manager account."""

    email: EmailStr = Field(..., description="Unique email address for manager")
    full_name: str = Field(..., description="Full legal name of manager")
    password: str = Field(..., description="Initial login password")
    warehouse_id: str = Field(..., description="Target warehouse ID assigned to manager")


class StaffCreateRequest(BaseModel):
    """Payload for Manager creating a Staff account."""

    email: EmailStr = Field(..., description="Unique email address for staff member")
    full_name: str = Field(..., description="Full legal name of staff member")
    password: str = Field(..., description="Initial login password")
    experience_tier: ExperienceTier = Field(
        default=ExperienceTier.ROOKIE, description="ROOKIE or EXPERIENCED tier"
    )
    function_roles: list[FunctionRole] = Field(
        default_factory=list, description="List of operational function roles"
    )


class StaffUpdateRequest(BaseModel):
    """Payload for Manager updating an existing Staff account."""

    full_name: str | None = Field(default=None, description="Updated full name")
    experience_tier: ExperienceTier | None = Field(
        default=None, description="Updated experience tier (ROOKIE or EXPERIENCED)"
    )
    function_roles: list[FunctionRole] | None = Field(
        default=None, description="Updated list of operational function roles"
    )


class ManagerDeactivateRequest(BaseModel):
    """Payload for Owner deactivating a Manager account with staff reassignment."""

    reassign_to_manager_id: str | None = Field(
        default=None, description="Target manager user ID to receive orphaned staff"
    )
