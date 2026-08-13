"""
inbox_model.py — Inbox shipment announcement model and domain enums.

Defines InboxShipment document schema stored in MongoDB inbox_shipments collection.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from pytz import timezone


class InboxStatus(str, Enum):
    """Status enumeration for incoming parcel announcements."""
    ANNOUNCED = "ANNOUNCED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    NEEDS_SPEC = "NEEDS_SPEC"


class InboxShipment(BaseModel):
    """
    Inbox shipment database document schema.

    Records incoming parcels announced by sellers prior to arrival.
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    seller_name: str = Field(..., description="Seller or vendor name announcing parcel")
    expected_items: list[dict[str, Any]] = Field(
        ..., description="List of expected product items [{name, quantity, upc}]"
    )
    tracking_number: str | None = Field(default=None, description="Carrier tracking number string")
    carrier: str | None = Field(default=None, description="Shipping carrier name (UPS, FedEx, USPS)")
    warehouse_id: str = Field(..., description="Destination warehouse ID")
    status: InboxStatus = Field(
        default=InboxStatus.ANNOUNCED, description="Shipment status"
    )
    comments: list[dict[str, Any]] = Field(
        default_factory=list, description="Comment thread for NEEDS_SPEC discussions"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC updated timestamp string",
    )
