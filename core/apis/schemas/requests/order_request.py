"""
order_request.py — Request schemas for order intake and packing operations.

Defines Pydantic models for manual order creation and packing confirmation.
"""

from pydantic import BaseModel, Field

from core.models.order_model import OrderItemSpec


class OrderCreateRequest(BaseModel):
    """Payload for manual order intake creation."""

    order_id: str = Field(..., description="Unique customer order reference ID (e.g. ORD-1001)")
    customer_name: str = Field(..., description="Customer full name")
    warehouse_id: str = Field(..., description="Fulfilling warehouse facility ID")
    items: list[OrderItemSpec] = Field(..., description="List of ordered line items")


class OrderPackRequest(BaseModel):
    """Payload for packing confirmation with weight and package dimensions."""

    packed_weight: float = Field(..., gt=0, description="Confirmed package weight (lbs)")
    width: float = Field(..., gt=0, description="Package width dimension (in)")
    height: float = Field(..., gt=0, description="Package height dimension (in)")
    length: float = Field(..., gt=0, description="Package length dimension (in)")
