"""
wms_response.py — Consolidated WMS API response schemas.

This file consolidates all WMS feature response schemas:
- api_key_response: API Key management response schemas
- audit_response: Audit log response schemas
- facility_response: Warehouse facility management response schemas
- health_response: Health check response schema
- inbox_response: Inbox announcement response schemas
- item_response: Item response schemas
- order_response: Order fulfillment response schemas
- query_response: Natural language query response schema
- report_response: Reporting and analytics response schemas
- storage_response: Storage location response schemas
- ticket_response: Ticket response schemas
- vision_response: Vision measurement response schema
- voice_response: Voice pipeline response schemas
- user_responses: User profile response schemas (from original user_responses.py)

All response classes can be imported directly from this module.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from core.models.wms_models import (
    DamageDetail,
    DraftStatus,
    InboxStatus,
    OrderItemSpec,
    OrderStatus,
    TicketStatus,
)


# ============================================================================
# API KEY RESPONSE SCHEMAS
# ============================================================================

class ApiKeyCreatedResponse(BaseModel):
    """Response payload returned ONCE upon key generation containing raw_key."""

    id: str = Field(..., description="API Key record ID")
    name: str = Field(..., description="Key name label")
    raw_key: str = Field(..., description="Raw secret API key string (returned ONLY ONCE)")
    prefix: str = Field(..., description="Display prefix")
    role: str = Field(..., description="Associated RBAC role")
    scopes: list[str] = Field(..., description="Permission scopes")
    created_at: str = Field(..., description="UTC creation timestamp string")


class ApiKeyItemResponse(BaseModel):
    """Response payload for listing API keys (without raw_key)."""

    id: str = Field(..., description="API Key record ID")
    name: str = Field(..., description="Key name label")
    prefix: str = Field(..., description="Display prefix")
    role: str = Field(..., description="Associated RBAC role")
    scopes: list[str] = Field(..., description="Permission scopes")
    is_active: bool = Field(..., description="Key active status flag")
    created_at: str = Field(..., description="UTC creation timestamp string")


class ApiKeyListResponse(BaseModel):
    """Response wrapper for listing API keys."""

    keys: list[ApiKeyItemResponse] = Field(..., description="List of API key items")


# ============================================================================
# AUDIT RESPONSE SCHEMAS
# ============================================================================

class AuditLogResponse(BaseModel):
    """Response payload representing audit log record."""

    id: str = Field(..., description="Audit log entry unique ID")
    actor_id: str = Field(..., description="Actor user ID")
    actor_email: str | None = Field(default=None, description="Actor email address")
    actor_role: str = Field(..., description="Actor RBAC role")
    action: str = Field(..., description="Mutation action name")
    collection: str = Field(..., description="Target database collection name")
    doc_id: str = Field(..., description="Target document ID string")
    before: dict[str, Any] | None = Field(default=None, description="State before mutation")
    after: dict[str, Any] | None = Field(default=None, description="State after mutation")
    timestamp: str = Field(..., description="UTC mutation timestamp string")


class AuditLogListResponse(BaseModel):
    """Response payload wrapper for querying audit logs."""

    logs: list[AuditLogResponse] = Field(..., description="List of audit log objects")
    total: int = Field(..., description="Total matching audit log record count")


# ============================================================================
# FACILITY RESPONSE SCHEMAS
# ============================================================================

class WarehouseResponse(BaseModel):
    """Response payload representing warehouse details."""

    id: str = Field(..., description="Warehouse unique ID string")
    code: str = Field(..., description="Unique warehouse short code")
    name: str = Field(..., description="Warehouse facility name")
    address: str | None = Field(default=None, description="Physical facility address")
    manager_id: str | None = Field(default=None, description="Assigned manager user ID")
    is_active: bool = Field(..., description="Warehouse active status flag")
    created_at: str = Field(..., description="UTC creation timestamp string")


class WarehouseListResponse(BaseModel):
    """Response payload wrapper for listing warehouse facilities."""

    warehouses: list[WarehouseResponse] = Field(..., description="List of warehouse facility objects")
    total: int = Field(..., description="Total matching warehouse record count")


# ============================================================================
# HEALTH RESPONSE SCHEMA
# ============================================================================

class HealthResponse(BaseModel):
    """
    Schema for system health check response payload.

    Provides status of the API service, database connectivity, and timestamp.
    """

    status: str = Field(..., description="Overall system health status (ok/error)")
    service: str = Field(..., description="Service identifier name")
    version: str = Field(..., description="Application semantic version")
    database: str = Field(..., description="Database connection status (connected/disconnected)")
    timestamp: str = Field(..., description="UTC ISO timestamp of health check")


# ============================================================================
# INBOX RESPONSE SCHEMAS
# ============================================================================

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


# ============================================================================
# ITEM RESPONSE SCHEMAS
# ============================================================================

class ItemResponse(BaseModel):
    """Response payload representing an individual scanned unit item."""

    id: str = Field(..., description="Item unique ID string")
    ticket_id: str = Field(..., description="Parent ticket ID")
    unit_seq: int = Field(..., description="Unit sequence index")
    barcode: str = Field(..., description="UPC barcode")
    product_name: str = Field(..., description="Product title")
    width: float = Field(..., description="Width dimension (in)")
    height: float = Field(..., description="Height dimension (in)")
    weight: float = Field(..., description="Weight (lbs)")
    image_url: str | None = Field(default=None, description="Image URL")
    damage: DamageDetail = Field(..., description="Damage details flag and note")
    status: TicketStatus = Field(..., description="Unit inventory status")
    warehouse_id: str = Field(..., description="Assigned warehouse ID")
    storage_location: str | None = Field(default=None, description="Storage location code")
    order_id: str | None = Field(default=None, description="Order ID if reserved/sold")
    logged_by: str = Field(..., description="Staff user ID logging the item")
    created_at: str = Field(..., description="UTC creation timestamp string")


class ItemListResponse(BaseModel):
    """Response wrapper for listing items."""

    items: list[ItemResponse] = Field(..., description="List of item objects")
    total: int = Field(..., description="Total matching record count")


# ============================================================================
# ORDER RESPONSE SCHEMAS
# ============================================================================

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


# ============================================================================
# QUERY RESPONSE SCHEMA
# ============================================================================

class NLQueryResponse(BaseModel):
    """Response payload for natural language query execution."""

    template_used: str = Field(..., description="Allow-listed aggregation query template ID")
    description: str = Field(..., description="Description of the template logic applied")
    query_text: str = Field(..., description="Original query prompt string")
    results: list[dict[str, Any]] = Field(..., description="Query result row records")


# ============================================================================
# REPORT RESPONSE SCHEMAS
# ============================================================================

class WarehouseSummaryMetrics(BaseModel):
    """Summary metrics per warehouse facility."""

    warehouse_id: str = Field(..., description="Warehouse ID string")
    todays_tickets: int = Field(..., description="Tickets generated today")
    todays_sold: int = Field(..., description="Items sold today")
    arrived_missed: int = Field(..., description="Unannounced arrivals (no_ticket_arrival=true)")


class ReportSummaryResponse(BaseModel):
    """Response payload for GET /reports/summary executive dashboard metrics."""

    date: str = Field(..., description="Report date string (YYYY-MM-DD)")
    todays_tickets: int = Field(..., description="Total system tickets created today")
    todays_sold: int = Field(..., description="Total system items sold today")
    arrived_missed: int = Field(..., description="Total unannounced arrivals count")
    per_warehouse: list[WarehouseSummaryMetrics] = Field(
        ..., description="Breakdown of summary metrics per warehouse"
    )


class StockSummaryItem(BaseModel):
    """Aggregated stock totals for a product in a warehouse."""

    barcode: str = Field(..., description="Product barcode")
    product_name: str = Field(..., description="Product description")
    warehouse_id: str = Field(..., description="Warehouse ID")
    on_hand: int = Field(..., description="Total units on hand (STORED + RESERVED)")
    available: int = Field(..., description="Units available for sale (STORED)")
    reserved: int = Field(..., description="Units currently reserved for orders")
    damaged: int = Field(..., description="Units marked damaged (non-sellable)")


class StockTotalsResponse(BaseModel):
    """Response payload for GET /reports/stock manager stock aggregation."""

    stock: list[StockSummaryItem] = Field(..., description="Aggregated product stock totals")
    total_on_hand: int = Field(..., description="Grand total units on hand across system")
    total_available: int = Field(..., description="Grand total units available")
    total_reserved: int = Field(..., description="Grand total units reserved")
    total_damaged: int = Field(..., description="Grand total units damaged")


class ReportFeedResponse(BaseModel):
    """Response payload for GET /reports/arrived-today and GET /reports/sold-today."""

    feed_type: str = Field(..., description="Feed type identifier (arrived_today / sold_today)")
    records: list[dict[str, Any]] = Field(..., description="Detail row records")
    total: int = Field(..., description="Total matching record count")


# ============================================================================
# STORAGE RESPONSE SCHEMAS
# ============================================================================

class StorageLocationResponse(BaseModel):
    """Response payload representing physical storage location."""

    id: str = Field(..., description="Storage location ID string")
    warehouse_id: str = Field(..., description="Warehouse ID")
    zone: str = Field(..., description="Zone code")
    rack: str = Field(..., description="Rack code")
    bin: str = Field(..., description="Bin code")
    location_code: str = Field(..., description="Full location string (e.g. A-04-12)")
    is_occupied: bool = Field(..., description="Occupied flag")
    created_at: str = Field(..., description="UTC creation timestamp string")


class StorageLocationListResponse(BaseModel):
    """Response wrapper for listing storage locations."""

    locations: list[StorageLocationResponse] = Field(..., description="List of storage locations")
    total: int = Field(..., description="Total matching record count")


# ============================================================================
# TICKET RESPONSE SCHEMAS
# ============================================================================

class TicketResponse(BaseModel):
    """Response payload representing ticket details."""

    id: str = Field(..., description="MongoDB ticket ID string")
    ticket_id: str = Field(..., description="Unique generated ticket identifier (e.g. RNO-20260813-001)")
    warehouse_id: str = Field(..., description="Assigned warehouse ID")
    inbox_id: str | None = Field(default=None, description="Matched inbox ID")
    tracking_number: str | None = Field(default=None, description="Tracking number")
    no_ticket_arrival: bool = Field(..., description="No ticket arrival flag")
    status: TicketStatus = Field(..., description="Current ticket status")
    arrived_by: str = Field(..., description="Staff user ID receiving arrival")
    approved_by: str | None = Field(default=None, description="Manager user ID approving ticket")
    storage_location: str | None = Field(default=None, description="Assigned storage location")
    created_at: str = Field(..., description="UTC creation timestamp string")


class TicketListResponse(BaseModel):
    """Response wrapper for listing tickets."""

    tickets: list[TicketResponse] = Field(..., description="List of ticket objects")
    total: int = Field(..., description="Total matching record count")


class ApprovalQueueResponse(BaseModel):
    """Response model for manager approval queue list."""

    pending_tickets: list[TicketResponse] = Field(..., description="List of tickets pending inspection approval")
    total: int = Field(..., description="Total count of tickets pending approval")


# ============================================================================
# VISION RESPONSE SCHEMA
# ============================================================================

class VisionMeasureResponse(BaseModel):
    """Response payload for OpenCV vision package dimension measurement."""

    width: float = Field(..., description="Estimated package width in inches")
    height: float = Field(..., description="Estimated package height in inches")
    weight: float = Field(default=0.0, description="Package weight (ALWAYS manual)")
    confidence: float = Field(..., description="Vision detection confidence score (0.0 to 1.0)")
    marker_found: bool = Field(..., description="Whether ArUco reference marker was detected")
    error: str | None = Field(default=None, description="Detection error message if marker missing")


# ============================================================================
# VOICE RESPONSE SCHEMAS
# ============================================================================

class TranscribeResponse(BaseModel):
    """Response payload for audio transcription."""

    transcript: str = Field(..., description="Transcribed audio text string")


class VoiceDraftResponse(BaseModel):
    """Response payload for voice parsed draft."""

    id: str = Field(..., description="Voice draft ID string")
    ticket_id: str = Field(..., description="Target ticket ID")
    transcript: str = Field(..., description="Audio transcript string")
    parsed_data: dict[str, Any] = Field(..., description="Extracted draft item fields")
    confidence_scores: dict[str, float] = Field(..., description="Per-field AI confidence scores")
    status: DraftStatus = Field(..., description="Draft status (DRAFT, CONFIRMED, DISCARDED)")
    created_at: str = Field(..., description="UTC creation timestamp string")


# ============================================================================
# USER RESPONSE SCHEMAS (from original user_responses.py)
# ============================================================================

class UserResponse(BaseModel):
    """
    Response model returned when the API sends user profile data.

    This model is used by endpoints such as register and get current user.
    Sensitive values such as hashed_password are intentionally excluded.
    """

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    mobile_number: str | None
    role: str
    status: str
    created_at: datetime


class LoginResponse(BaseModel):
    """
    Response model returned after a successful login.

    The API returns a JWT access token and a nested user profile object.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Simple response model used when only a text message is returned."""

    message: str
