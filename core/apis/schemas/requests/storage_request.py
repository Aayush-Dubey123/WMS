"""
storage_request.py — Request schemas for storage location creation and ticket storage assignment.

Defines Pydantic models for physical storage location configuration and assignment.
"""

from pydantic import BaseModel, Field


class StorageLocationCreateRequest(BaseModel):
    """Payload for creating a new physical storage location bin."""

    warehouse_id: str = Field(..., description="Target warehouse facility ID")
    zone: str = Field(..., description="Storage zone (e.g. Zone A)")
    rack: str = Field(..., description="Storage rack (e.g. Rack 04)")
    bin: str = Field(..., description="Storage bin (e.g. Bin 12)")


class StoreTicketRequest(BaseModel):
    """Payload for assigning storage location to a ticket and its units."""

    storage_location: str = Field(..., description="Target storage location code (e.g. A-04-12)")
