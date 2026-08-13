"""
ticket_model.py — Ticket persistence model and fixed status enums.

Defines Ticket document schema stored in MongoDB tickets collection.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from pytz import timezone


class TicketStatus(str, Enum):
    """Fixed Ticket/Item status state machine enum."""
    ANNOUNCED = "ANNOUNCED"
    ACCEPTED = "ACCEPTED"
    ARRIVED = "ARRIVED"
    PENDING_INSPECTION = "PENDING_INSPECTION"
    INSPECTED = "INSPECTED"
    SHIPMENT_ARRIVED = "SHIPMENT_ARRIVED"
    STORED = "STORED"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    DECLINED = "DECLINED"
    NEEDS_SPEC = "NEEDS_SPEC"
    DAMAGED = "DAMAGED"


class Ticket(BaseModel):
    """
    Ticket database persistence document schema.

    Represents a ticket created on arrival for an incoming parcel batch.
    Format: {WH}-{YYYYMMDD}-{SEQ} (e.g. RNO-20260813-014).
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    ticket_id: str = Field(..., description="Unique generated ticket identifier string")
    warehouse_id: str = Field(..., description="Assigned warehouse facility ID")
    inbox_id: str | None = Field(default=None, description="Matched inbox shipment ID if available")
    tracking_number: str | None = Field(default=None, description="Carrier tracking number")
    no_ticket_arrival: bool = Field(
        default=False, description="Flag indicating arrival without seller pre-announcement ticket"
    )
    status: TicketStatus = Field(
        default=TicketStatus.ARRIVED, description="Current ticket lifecycle status"
    )
    arrived_by: str = Field(..., description="Staff user ID who received the arrival")
    approved_by: str | None = Field(default=None, description="Manager user ID who approved inspection")
    storage_location: str | None = Field(default=None, description="Assigned storage location string")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC updated timestamp string",
    )
