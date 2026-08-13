"""
facility_request.py — Request schemas for warehouse facility management endpoints.

Defines Pydantic models for Warehouse creation and updates.
"""


from pydantic import BaseModel, Field


class WarehouseCreateRequest(BaseModel):
    """Payload for creating a new Warehouse facility."""

    code: str = Field(..., description="Unique warehouse short code (e.g. RNO, LAX)", example="RNO")
    name: str = Field(..., description="Facility name", example="Reno Distribution Center")
    address: str | None = Field(default=None, description="Physical address")


class WarehouseUpdateRequest(BaseModel):
    """Payload for updating an existing Warehouse facility."""

    name: str | None = Field(default=None, description="Updated facility name")
    address: str | None = Field(default=None, description="Updated physical address")
    manager_id: str | None = Field(default=None, description="Assigned manager user ID")
    is_active: bool | None = Field(default=None, description="Warehouse active status flag")
