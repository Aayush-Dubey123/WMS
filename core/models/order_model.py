"""
order_model.py — Order persistence model and status enums.

Defines Order document schema stored in MongoDB orders collection.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from pytz import timezone


class OrderStatus(str, Enum):
    """Order fulfillment status state machine enum."""
    PENDING = "PENDING"
    RESERVED = "RESERVED"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class OrderItemSpec(BaseModel):
    """Sub-schema for ordered line items."""

    barcode: str = Field(..., description="Target product barcode / UPC code")
    product_name: str = Field(..., description="Product title description")
    quantity: int = Field(..., ge=1, description="Quantity ordered")


class Order(BaseModel):
    """
    Order database persistence document schema.

    Represents customer orders fulfilled from warehouse stock.
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    order_id: str = Field(..., description="Unique customer order ID string (e.g. ORD-1001)")
    customer_name: str = Field(..., description="Customer full name")
    warehouse_id: str = Field(..., description="Fulfilling warehouse facility ID")
    items: list[OrderItemSpec] = Field(..., description="List of ordered line items")
    status: OrderStatus = Field(
        default=OrderStatus.PENDING, description="Current order fulfillment status"
    )
    packed_weight: float | None = Field(default=None, description="Confirmed packed weight in lbs")
    packed_dims: dict[str, float] | None = Field(
        default=None, description="Confirmed package dimensions {width, height, length}"
    )
    tracking_number: str | None = Field(default=None, description="Carrier tracking number")
    label_url: str | None = Field(default=None, description="Generated carrier shipping label URL")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC updated timestamp string",
    )
