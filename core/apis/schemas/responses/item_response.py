"""
item_response.py â€” Response schemas for item endpoints.

Defines ItemResponse and ItemListResponse models.
"""


from pydantic import BaseModel, Field

from core.models.wms_models import DamageDetail
from core.models.wms_models import TicketStatus


class ItemResponse(BaseModel):
    """Response payload representing an individual scanned unit item."""

    id: str = Field(..., description="Item unique ID string")
    ticket_id: str = Field(..., description="Parent ticket ID")
    unit_seq: int = Field(..., description="Unit sequence index")
    barcode: str = Field(..., description="UPC barcode")
    product_name: str = Field(..., description="Product title")
    width: float = Field(..., description="Width dimension (in)")
    height: float = Field(..., description="Height dimension (in)")
    weight: float = Field(..., description="Weight (lbs)")
    image_url: str | None = Field(default=None, description="Image URL")
    damage: DamageDetail = Field(..., description="Damage details flag and note")
    status: TicketStatus = Field(..., description="Unit inventory status")
    warehouse_id: str = Field(..., description="Assigned warehouse ID")
    storage_location: str | None = Field(default=None, description="Storage location code")
    order_id: str | None = Field(default=None, description="Order ID if reserved/sold")
    logged_by: str = Field(..., description="Staff user ID logging the item")
    created_at: str = Field(..., description="UTC creation timestamp string")


class ItemListResponse(BaseModel):
    """Response wrapper for listing items."""

    items: list[ItemResponse] = Field(..., description="List of item objects")
    total: int = Field(..., description="Total matching record count")

