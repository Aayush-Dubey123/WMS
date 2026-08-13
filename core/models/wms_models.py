"""
wms_models.py — Consolidated WMS domain models and enums.

Merges all WMS entity Pydantic persistence models into a single module:
- ApiKey: API key document schema
- AuditLog: Audit log record schema
- InboxStatus, InboxShipment: Inbox shipment schema
- DamageDetail, Item: Item document schema
- OrderStatus, OrderItemSpec, Order: Order document schema
- StorageLocation: Storage location schema
- TicketStatus, Ticket: Ticket document schema
- DraftStatus, VoiceDraft: Voice draft document schema
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from pytz import timezone


# ====== API KEY MODEL ======

class ApiKey(BaseModel):
    """API Key database persistence document schema."""

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    name: str = Field(..., description="Key label or client application name")
    key_hash: str = Field(..., description="Bcrypt/SHA256 hash of raw API key")
    prefix: str = Field(..., description="Display prefix string (e.g. wms_live_abc123)")
    role: str = Field(..., description="Associated RBAC role (OWNER, MANAGER, STAFF)")
    scopes: list[str] = Field(
        default_factory=lambda: ["read"], description="Allowed permission scopes ('read', 'write')"
    )
    is_active: bool = Field(default=True, description="API key active status flag")
    created_by: str = Field(..., description="User ID who generated key")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )


# ====== AUDIT LOG MODEL ======

class AuditLog(BaseModel):
    """Audit log record persistence schema."""

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    actor_id: str = Field(..., description="ID of user performing action")
    actor_email: str | None = Field(default=None, description="Email of user performing action")
    actor_role: str = Field(..., description="Role of user performing action")
    action: str = Field(..., description="Mutation action name (e.g. CREATE, UPDATE, DELETE)")
    collection: str = Field(..., description="Target database collection modified")
    doc_id: str = Field(..., description="Target document ID modified")
    before: dict[str, Any] | None = Field(
        default=None, description="Document state before mutation"
    )
    after: dict[str, Any] | None = Field(
        default=None, description="Document state after mutation"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC mutation timestamp string",
    )


# ====== INBOX MODELS ======

class InboxStatus(str, Enum):
    """Status enumeration for incoming parcel announcements."""
    ANNOUNCED = "ANNOUNCED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    NEEDS_SPEC = "NEEDS_SPEC"


class InboxShipment(BaseModel):
    """Inbox shipment database document schema."""

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


# ====== ITEM MODELS ======

class DamageDetail(BaseModel):
    """Sub-schema for recording item physical damage details."""

    flag: bool = Field(default=False, description="Flag indicating physical damage presence")
    note: str | None = Field(default=None, description="Detailed damage inspection description")


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


class Item(BaseModel):
    """Item database persistence document schema."""

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


# ====== ORDER MODELS ======

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
    """Order database persistence document schema."""

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


# ====== STORAGE LOCATION MODEL ======

class StorageLocation(BaseModel):
    """Storage location document schema."""

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    warehouse_id: str = Field(..., description="Target warehouse facility ID")
    zone: str = Field(..., description="Storage zone code (e.g. Zone A)")
    rack: str = Field(..., description="Storage rack code (e.g. Rack 04)")
    bin: str = Field(..., description="Storage bin code (e.g. Bin 12)")
    location_code: str = Field(..., description="Combined location code string (e.g. A-04-12)")
    is_occupied: bool = Field(default=False, description="Flag indicating if location is currently occupied")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC updated timestamp string",
    )


# ====== TICKET MODEL ======

class Ticket(BaseModel):
    """Ticket database persistence document schema."""

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


# ====== VOICE DRAFT MODELS ======

class DraftStatus(str, Enum):
    """Voice draft lifecycle status enum."""
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    DISCARDED = "DISCARDED"


class VoiceDraft(BaseModel):
    """Voice draft database document schema."""

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    user_id: str = Field(..., description="ID of staff user recording voice")
    warehouse_id: str = Field(..., description="Warehouse facility ID")
    ticket_id: str = Field(..., description="Target ticket ID string")
    transcript: str = Field(..., description="Transcribed audio text")
    parsed_data: dict[str, Any] = Field(
        ..., description="Extracted fields {product_name, width, height, weight, fragile, damage}"
    )
    confidence_scores: dict[str, float] = Field(
        default_factory=dict, description="Per-field AI confidence scores (0.0 to 1.0)"
    )
    status: DraftStatus = Field(
        default=DraftStatus.DRAFT, description="Draft lifecycle status"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC creation timestamp string",
    )
