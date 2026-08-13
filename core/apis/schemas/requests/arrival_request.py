"""
arrival_request.py — Request schema for arrival processing.

Defines Pydantic model for matching tracking numbers or flagging unannounced arrivals.
"""


from pydantic import BaseModel, Field


class ArrivalCreateRequest(BaseModel):
    """Payload for logging arrival of a parcel at warehouse."""

    warehouse_id: str = Field(..., description="Receiving warehouse facility ID")
    tracking_number: str | None = Field(
        default=None, description="Scanned carrier tracking number"
    )
    no_ticket_arrival: bool = Field(
        default=False, description="Flag set to True if parcel arrived without prior announcement ticket"
    )
