"""
order_response.py â€” Response schemas for order fulfillment endpoints.

Defines OrderResponse, OrderListResponse, PicklistResponse, and ShippingLabelResponse models.
"""

from pydantic import BaseModel, Field

from core.models.wms_models import OrderItemSpec, OrderStatus


class OrderResponse(BaseModel):
    """Response payload representing customer order details."""

    id: str = Field(..., description="Order unique ID string")
    order_id: str = Field(..., description="Customer order ID reference string")
    customer_name: str = Field(..., description="Customer full name")
    warehouse_id: str = Field(..., description="Assigned warehouse facility ID")
    items: list[OrderItemSpec] = Field(..., description="Ordered line items")
    status: OrderStatus = Field(..., description="Current order status")
    packed_weight: float | None = Field(default=None, description="Packed weight")
    packed_dims: dict[str, float] | None = Field(default=None, description="Packed dimensions")
    tracking_number: str | None = Field(default=None, description="Tracking number")
    label_url: str | None = Field(default=None, description="Shipping label URL")
    created_at: str = Field(..., description="UTC creation timestamp string")


class OrderListResponse(BaseModel):
    """Response wrapper for listing orders."""

    orders: list[OrderResponse] = Field(..., description="List of order objects")
    total: int = Field(..., description="Total matching record count")


class PicklistItem(BaseModel):
    """Sub-schema representing a item pick location on picklist."""

    item_id: str = Field(..., description="Reserved item unit ID")
    ticket_id: str = Field(..., description="Origin ticket ID")
    unit_seq: int = Field(..., description="Unit sequence index")
    barcode: str = Field(..., description="Product barcode")
    product_name: str = Field(..., description="Product title description")
    storage_location: str = Field(..., description="Physical storage bin location (e.g. A-04-12)")


class PicklistResponse(BaseModel):
    """Response payload for order picklist containing item bin storage locations."""

    order_id: str = Field(..., description="Target order ID reference")
    warehouse_id: str = Field(..., description="Warehouse facility ID")
    picklist: list[PicklistItem] = Field(..., description="List of items and their storage bin locations")


class ShippingLabelResponse(BaseModel):
    """Response payload for carrier shipping label generation stub."""

    order_id: str = Field(..., description="Target order ID reference")
    carrier: str = Field(..., description="Carrier name (e.g. EasyPost / Shippo Stub)")
    tracking_number: str = Field(..., description="Generated tracking number string")
    label_url: str = Field(..., description="URL to download printable shipping label")

