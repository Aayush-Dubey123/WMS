"""
api_key_response.py — Response schema for API Key management endpoints.

Defines Pydantic response models for API key creation and listing.
"""

from pydantic import BaseModel, Field


class ApiKeyCreatedResponse(BaseModel):
    """Response payload returned ONCE upon key generation containing raw_key."""

    id: str = Field(..., description="API Key record ID")
    name: str = Field(..., description="Key name label")
    raw_key: str = Field(..., description="Raw secret API key string (returned ONLY ONCE)")
    prefix: str = Field(..., description="Display prefix")
    role: str = Field(..., description="Associated RBAC role")
    scopes: list[str] = Field(..., description="Permission scopes")
    created_at: str = Field(..., description="UTC creation timestamp string")


class ApiKeyItemResponse(BaseModel):
    """Response payload for listing API keys (without raw_key)."""

    id: str = Field(..., description="API Key record ID")
    name: str = Field(..., description="Key name label")
    prefix: str = Field(..., description="Display prefix")
    role: str = Field(..., description="Associated RBAC role")
    scopes: list[str] = Field(..., description="Permission scopes")
    is_active: bool = Field(..., description="Key active status flag")
    created_at: str = Field(..., description="UTC creation timestamp string")


class ApiKeyListResponse(BaseModel):
    """Response wrapper for listing API keys."""

    keys: list[ApiKeyItemResponse] = Field(..., description="List of API key items")
