"""
storage_response.py — Response schemas for storage location endpoints.

Defines StorageLocationResponse and StorageLocationListResponse models.
"""


from pydantic import BaseModel, Field


class StorageLocationResponse(BaseModel):
    """Response payload representing physical storage location."""

    id: str = Field(..., description="Storage location ID string")
    warehouse_id: str = Field(..., description="Warehouse ID")
    zone: str = Field(..., description="Zone code")
    rack: str = Field(..., description="Rack code")
    bin: str = Field(..., description="Bin code")
    location_code: str = Field(..., description="Full location string (e.g. A-04-12)")
    is_occupied: bool = Field(..., description="Occupied flag")
    created_at: str = Field(..., description="UTC creation timestamp string")


class StorageLocationListResponse(BaseModel):
    """Response wrapper for listing storage locations."""

    locations: list[StorageLocationResponse] = Field(..., description="List of storage locations")
    total: int = Field(..., description="Total matching record count")
