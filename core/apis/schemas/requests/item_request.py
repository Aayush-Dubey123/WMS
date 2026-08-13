"""
item_request.py â€” Request schemas for item barcode scanning and inspection logging.

Defines Pydantic model for scanning individual item units.
"""


from pydantic import BaseModel, Field

from core.models.wms_models import DamageDetail


class ItemLogRequest(BaseModel):
    """Payload for barcode scan item logging under a ticket."""

    barcode: str = Field(..., description="Scanned UPC or barcode string")
    product_name: str = Field(..., description="Product title description")
    width: float = Field(..., description="Package width dimension (inches)")
    height: float = Field(..., description="Package height dimension (inches)")
    weight: float = Field(..., description="Package weight (lbs)")
    image_url: str | None = Field(default=None, description="Optional uploaded image URL")
    damage: DamageDetail | None = Field(
        default_factory=DamageDetail, description="Physical damage details flag and note"
    )

