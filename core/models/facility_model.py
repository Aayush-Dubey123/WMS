"""
facility_model.py — Warehouse facility persistence model.

Defines Warehouse document schema stored in MongoDB warehouses collection.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from pytz import timezone


class Warehouse(BaseModel):
    """
    Warehouse database persistence document schema.

    Stores physical warehouse locations, warehouse code, and assigned manager ID.
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    code: str = Field(..., description="Unique warehouse short code identifier (e.g. RNO, LAX)")
    name: str = Field(..., description="Full warehouse facility name")
    address: str | None = Field(default=None, description="Physical address string")
    manager_id: str | None = Field(default=None, description="Assigned manager user ID")
    is_active: bool = Field(default=True, description="Warehouse active status flag")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC updated timestamp string",
    )
