"""
inbox_request.py — Request schemas for inbox announcement endpoints.

Defines Pydantic models for seller shipment announcements and revert requests.
"""

from typing import Any

from pydantic import BaseModel, Field


class InboxAnnounceRequest(BaseModel):
    """Payload for announcing an incoming parcel shipment."""

    seller_name: str = Field(..., description="Seller or vendor name")
    expected_items: list[dict[str, Any]] = Field(
        ..., description="List of expected products [{name, quantity, upc}]"
    )
    tracking_number: str | None = Field(default=None, description="Carrier tracking number string")
    carrier: str | None = Field(default=None, description="Carrier name (UPS, FedEx, USPS)")
    warehouse_id: str = Field(..., description="Destination warehouse facility ID")


class InboxRevertRequest(BaseModel):
    """Payload for reverting an inbox shipment to NEEDS_SPEC state with comment."""

    comment: str = Field(..., description="Reason / comment for requesting specification update")
