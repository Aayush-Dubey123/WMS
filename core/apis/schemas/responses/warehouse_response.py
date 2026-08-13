"""
warehouse_response.py — Response schemas for warehouse management endpoints.

Defines WarehouseResponse and WarehouseListResponse models.
"""


from pydantic import BaseModel, Field


class WarehouseResponse(BaseModel):
    """Response payload representing warehouse details."""

    id: str = Field(..., description="Warehouse unique ID string")
    code: str = Field(..., description="Unique warehouse short code")
    name: str = Field(..., description="Warehouse facility name")
    address: str | None = Field(default=None, description="Physical facility address")
    manager_id: str | None = Field(default=None, description="Assigned manager user ID")
    is_active: bool = Field(..., description="Warehouse active status flag")
    created_at: str = Field(..., description="UTC creation timestamp string")


class WarehouseListResponse(BaseModel):
    """Response payload wrapper for listing warehouse facilities."""

    warehouses: list[WarehouseResponse] = Field(..., description="List of warehouse facility objects")
    total: int = Field(..., description="Total matching warehouse record count")
