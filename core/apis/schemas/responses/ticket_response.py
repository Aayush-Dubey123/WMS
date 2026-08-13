"""
ticket_response.py — Response schemas for ticket endpoints.

Defines TicketResponse, TicketListResponse, and ApprovalQueueResponse models.
"""


from pydantic import BaseModel, Field

from core.models.ticket_model import TicketStatus


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
