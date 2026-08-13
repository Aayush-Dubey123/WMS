"""
api_key_model.py — API Key persistence model.

Defines ApiKey document schema stored in MongoDB api_keys collection.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from pytz import timezone


class ApiKey(BaseModel):
    """
    API Key database persistence document schema.

    Stores hashed external API keys, permission scopes, and creator details.
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    name: str = Field(..., description="Key label or client application name")
    key_hash: str = Field(..., description="Bcrypt/SHA256 hash of raw API key")
    prefix: str = Field(..., description="Display prefix string (e.g. wms_live_abc123)")
    role: str = Field(..., description="Associated RBAC role (OWNER, MANAGER, STAFF)")
    scopes: list[str] = Field(
        default_factory=lambda: ["read"], description="Allowed permission scopes ('read', 'write')"
    )
    is_active: bool = Field(default=True, description="API key active status flag")
    created_by: str = Field(..., description="User ID who generated key")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
