"""
api_key_request.py — Request schema for API Key generation.

Defines Pydantic request model for creating scoped API keys.
"""


from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    """Payload for API key creation."""

    name: str = Field(..., min_length=2, description="Key label or integration name")
    role: str = Field(default="STAFF", description="Associated RBAC role (OWNER, MANAGER, STAFF)")
    scopes: list[str] = Field(
        default_factory=lambda: ["read"], description="Allowed permission scopes ('read', 'write')"
    )
