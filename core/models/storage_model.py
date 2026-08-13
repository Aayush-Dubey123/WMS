"""
storage_model.py — Storage location persistence document schema.

Defines StorageLocation document schema stored in MongoDB storage_locations collection.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from pytz import timezone


class StorageLocation(BaseModel):
    """
    Storage location document schema.

    Represents physical warehouse storage bins (Zone, Rack, Bin).
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    warehouse_id: str = Field(..., description="Target warehouse facility ID")
    zone: str = Field(..., description="Storage zone code (e.g. Zone A)")
    rack: str = Field(..., description="Storage rack code (e.g. Rack 04)")
    bin: str = Field(..., description="Storage bin code (e.g. Bin 12)")
    location_code: str = Field(..., description="Combined location code string (e.g. A-04-12)")
    is_occupied: bool = Field(default=False, description="Flag indicating if location is currently occupied")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC updated timestamp string",
    )
