"""
item_model.py — Item persistence document schema and damage sub-schema.

Defines Item document schema stored in MongoDB items collection.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from pytz import timezone

from core.models.ticket_model import TicketStatus


class DamageDetail(BaseModel):
    """Sub-schema for recording item physical damage details."""

    flag: bool = Field(default=False, description="Flag indicating physical damage presence")
    note: str | None = Field(default=None, description="Detailed damage inspection description")


class Item(BaseModel):
    """
    Item database persistence document schema.

    Represents an individual physical unit logged under a Ticket.
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    ticket_id: str = Field(..., description="Parent ticket identifier string")
    unit_seq: int = Field(..., description="Sequential unit index within ticket (1..N)")
    barcode: str = Field(..., description="Product barcode / UPC scanned code")
    product_name: str = Field(..., description="Scanned product title or description")
    width: float = Field(..., description="Package width dimension in inches")
    height: float = Field(..., description="Package height dimension in inches")
    weight: float = Field(..., description="Package weight in lbs")
    image_url: str | None = Field(default=None, description="Optional stored image URL")
    damage: DamageDetail = Field(
        default_factory=DamageDetail, description="Physical damage details"
    )
    status: TicketStatus = Field(
        default=TicketStatus.PENDING_INSPECTION, description="Individual unit inventory status"
    )
    warehouse_id: str = Field(..., description="Assigned warehouse ID")
    storage_location: str | None = Field(default=None, description="Assigned zone/rack/bin code")
    order_id: str | None = Field(default=None, description="Attached order ID when RESERVED/SOLD")
    logged_by: str = Field(..., description="Staff user ID who logged the item")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC updated timestamp string",
    )
