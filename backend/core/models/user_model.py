"""
user_model.py — User persistence model and domain enums.

Defines User document schema stored in MongoDB users collection.
Supports Owner -> Manager -> Staff role chain and experience tiers.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field
from pytz import timezone


class UserRole(str, Enum):
    """User role enumeration for RBAC authorization."""
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    STAFF = "STAFF"


class ExperienceTier(str, Enum):
    """Staff experience tier enumeration."""
    ROOKIE = "ROOKIE"
    EXPERIENCED = "EXPERIENCED"


class FunctionRole(str, Enum):
    """Staff operational function role assignment enumeration."""
    LISTING = "LISTING"
    PACKING = "PACKING"
    RECEIVING = "RECEIVING"
    INSPECTION = "INSPECTION"
    STORAGE = "STORAGE"


class UserStatus(str, Enum):
    """User account lifecycle status."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class User(BaseModel):
    """
    User database persistence document schema.

    Stores authentication details, assigned warehouse, roles, and experience tier.
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    email: EmailStr = Field(..., description="Unique email address for authentication")
    full_name: str = Field(..., description="User full legal or display name")
    hashed_password: str = Field(..., description="Argon2/Bcrypt hashed password")
    role: UserRole = Field(..., description="System RBAC role (OWNER, MANAGER, STAFF)")
    warehouse_id: str | None = Field(
        default=None, description="Assigned warehouse ID (None for OWNER)"
    )
    experience_tier: ExperienceTier | None = Field(
        default=None, description="Experience tier for STAFF (ROOKIE or EXPERIENCED)"
    )
    function_roles: list[FunctionRole] = Field(
        default_factory=list, description="Assigned functional duty roles"
    )
    status: UserStatus = Field(
        default=UserStatus.ACTIVE, description="User account active status"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC updated timestamp string",
    )
