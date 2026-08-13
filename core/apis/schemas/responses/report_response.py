"""
report_response.py — Response schemas for reporting and analytics endpoints.

Defines Pydantic models for executive summary metrics, detail feeds, and stock totals.
"""

from typing import Any

from pydantic import BaseModel, Field


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
