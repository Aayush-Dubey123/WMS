"""
inbox_response.py â€” Response schemas for inbox endpoints.

Defines InboxResponse and InboxListResponse models.
"""

from typing import Any

from pydantic import BaseModel, Field

from core.models.wms_models import InboxStatus


class InboxResponse(BaseModel):
    """Response payload for inbox shipment announcement."""

    id: str = Field(..., description="Inbox shipment unique ID")
    seller_name: str = Field(..., description="Seller name")
    expected_items: list[dict[str, Any]] = Field(..., description="Expected items list")
    tracking_number: str | None = Field(default=None, description="Tracking number")
    carrier: str | None = Field(default=None, description="Carrier name")
    warehouse_id: str = Field(..., description="Destination warehouse ID")
    status: InboxStatus = Field(..., description="Shipment status")
    comments: list[dict[str, Any]] = Field(default_factory=list, description="Comments thread")
    created_at: str = Field(..., description="UTC creation timestamp string")


class InboxListResponse(BaseModel):
    """Response wrapper for listing inbox announcements."""

    shipments: list[InboxResponse] = Field(..., description="List of inbox shipments")
    total: int = Field(..., description="Total record count")

