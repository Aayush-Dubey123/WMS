"""
wms_request.py — Consolidated WMS API request schemas.

This file consolidates all WMS feature request schemas:
- api_key_request: API Key generation request
- arrival_request: Arrival processing requests
- facility_request: Warehouse facility management requests
- inbox_request: Inbox announcement requests
- item_request: Item barcode scanning requests
- order_request: Order intake and packing requests
- query_request: Natural language query request
- storage_request: Storage location creation and assignment requests
- voice_request: Voice pipeline requests

All request classes can be imported directly from this module.
"""

from typing import Any

from pydantic import BaseModel, Field

from core.models.wms_models import DamageDetail, OrderItemSpec


# ============================================================================
# API KEY REQUEST SCHEMAS
# ============================================================================

class ApiKeyCreateRequest(BaseModel):
    """Payload for API key creation."""

    name: str = Field(..., min_length=2, description="Key label or integration name")
    role: str = Field(default="STAFF", description="Associated RBAC role (OWNER, MANAGER, STAFF)")
    scopes: list[str] = Field(
        default_factory=lambda: ["read"], description="Allowed permission scopes ('read', 'write')"
    )


# ============================================================================
# ARRIVAL REQUEST SCHEMAS
# ============================================================================

class ArrivalCreateRequest(BaseModel):
    """Payload for logging arrival of a parcel at warehouse."""

    warehouse_id: str = Field(..., description="Receiving warehouse facility ID")
    tracking_number: str | None = Field(
        default=None, description="Scanned carrier tracking number"
    )
    no_ticket_arrival: bool = Field(
        default=False, description="Flag set to True if parcel arrived without prior announcement ticket"
    )


# ============================================================================
# FACILITY REQUEST SCHEMAS
# ============================================================================

class WarehouseCreateRequest(BaseModel):
    """Payload for creating a new Warehouse facility."""

    code: str = Field(..., description="Unique warehouse short code (e.g. RNO, LAX)", example="RNO")
    name: str = Field(..., description="Facility name", example="Reno Distribution Center")
    address: str | None = Field(default=None, description="Physical address")


class WarehouseUpdateRequest(BaseModel):
    """Payload for updating an existing Warehouse facility."""

    name: str | None = Field(default=None, description="Updated facility name")
    address: str | None = Field(default=None, description="Updated physical address")
    manager_id: str | None = Field(default=None, description="Assigned manager user ID")
    is_active: bool | None = Field(default=None, description="Warehouse active status flag")


# ============================================================================
# INBOX REQUEST SCHEMAS
# ============================================================================

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


# ============================================================================
# ITEM REQUEST SCHEMAS
# ============================================================================

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


# ============================================================================
# ORDER REQUEST SCHEMAS
# ============================================================================

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


# ============================================================================
# QUERY REQUEST SCHEMAS
# ============================================================================

class NLQueryRequest(BaseModel):
    """Payload for natural language stock query."""

    query: str = Field(..., min_length=2, description="Natural language search prompt (e.g. 'How many damaged widgets in Reno?')")


# ============================================================================
# STORAGE REQUEST SCHEMAS
# ============================================================================

class StorageLocationCreateRequest(BaseModel):
    """Payload for creating a new physical storage location bin."""

    warehouse_id: str = Field(..., description="Target warehouse facility ID")
    zone: str = Field(..., description="Storage zone (e.g. Zone A)")
    rack: str = Field(..., description="Storage rack (e.g. Rack 04)")
    bin: str = Field(..., description="Storage bin (e.g. Bin 12)")


class StoreTicketRequest(BaseModel):
    """Payload for assigning storage location to a ticket and its units."""

    storage_location: str = Field(..., description="Target storage location code (e.g. A-04-12)")


# ============================================================================
# VOICE REQUEST SCHEMAS
# ============================================================================

class VoiceParseRequest(BaseModel):
    """Payload for LLM transcript parsing."""

    ticket_id: str = Field(..., description="Target ticket ID")
    transcript: str = Field(..., description="Transcribed voice audio text string")


class VoiceConfirmRequest(BaseModel):
    """Payload for confirming a voice draft."""

    barcode: str = Field(..., description="Confirmed product barcode / UPC code")
    override_weight: float = Field(..., gt=0, description="Manual confirmed weight (lbs)")
