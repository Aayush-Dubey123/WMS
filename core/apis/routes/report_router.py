"""
report_router.py — Reporting, dashboard analytics, and file export routes.

Exposes endpoints for GET /reports/summary, GET /reports/arrived-today, GET /reports/sold-today,
GET /reports/stock, and GET /reports/export (CSV & XLSX).
"""


from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from commons.auth import require_roles
from core import logger
from core.apis.schemas.responses.report_response import (
    ReportFeedResponse,
    ReportSummaryResponse,
    StockTotalsResponse,
)
from core.controllers.report_controller import ReportController

report_router = APIRouter(prefix="/reports", tags=["Reporting & Export"])
logging = logger(__name__)


@report_router.get(
    "/summary",
    status_code=status.HTTP_200_OK,
    response_model=ReportSummaryResponse,
)
async def get_summary(
    date: str | None = Query(None, description="Target date in YYYY-MM-DD format"),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Retrieve executive dashboard summary metrics (todays_tickets, todays_sold, arrived_missed).

    Args:
        date (Optional[str]): Target date query parameter.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        ReportSummaryResponse: Executive dashboard summary metrics payload.
    """
    try:
        logging.info("Calling GET /reports/summary endpoint")
        response = await ReportController().get_summary(target_date=date, current_user=current_user)
        return ReportSummaryResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /reports/summary endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /reports/summary endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@report_router.get(
    "/arrived-today",
    status_code=status.HTTP_200_OK,
    response_model=ReportFeedResponse,
)
async def get_arrived_today(
    date: str | None = Query(None, description="Target date in YYYY-MM-DD format"),
    warehouse_id: str | None = Query(None, description="Optional warehouse ID filter"),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Retrieve detail feed of parcels/tickets arrived on target date.

    Args:
        date (Optional[str]): Target date query.
        warehouse_id (Optional[str]): Warehouse filter.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        ReportFeedResponse: Detail feed of arrived tickets.
    """
    try:
        logging.info("Calling GET /reports/arrived-today endpoint")
        response = await ReportController().get_arrived_today(
            target_date=date,
            current_user=current_user,
            warehouse_id=warehouse_id,
        )
        return ReportFeedResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /reports/arrived-today endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /reports/arrived-today endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@report_router.get(
    "/sold-today",
    status_code=status.HTTP_200_OK,
    response_model=ReportFeedResponse,
)
async def get_sold_today(
    date: str | None = Query(None, description="Target date in YYYY-MM-DD format"),
    warehouse_id: str | None = Query(None, description="Optional warehouse ID filter"),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Retrieve detail feed of item units sold on target date.

    Args:
        date (Optional[str]): Target date query.
        warehouse_id (Optional[str]): Warehouse filter.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        ReportFeedResponse: Detail feed of sold items.
    """
    try:
        logging.info("Calling GET /reports/sold-today endpoint")
        response = await ReportController().get_sold_today(
            target_date=date,
            current_user=current_user,
            warehouse_id=warehouse_id,
        )
        return ReportFeedResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /reports/sold-today endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /reports/sold-today endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@report_router.get(
    "/stock",
    status_code=status.HTTP_200_OK,
    response_model=StockTotalsResponse,
)
async def get_stock_totals(
    warehouse_id: str | None = Query(None, description="Optional warehouse ID filter"),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Retrieve manager stock totals aggregation (on-hand, available, reserved, damaged per product).

    Args:
        warehouse_id (Optional[str]): Warehouse ID filter.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        StockTotalsResponse: Aggregated stock totals.
    """
    try:
        logging.info("Calling GET /reports/stock endpoint")
        response = await ReportController().get_stock_totals(
            current_user=current_user,
            warehouse_id=warehouse_id,
        )
        return StockTotalsResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /reports/stock endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /reports/stock endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@report_router.get(
    "/export",
    status_code=status.HTTP_200_OK,
)
async def export_report(
    report_type: str = Query(..., description="Report type (arrived, sold, stock)"),
    format: str = Query("csv", description="File format (csv or xlsx)"),
    date: str | None = Query(None, description="Target date (YYYY-MM-DD)"),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Export report feed as downloadable file stream (.csv or .xlsx).

    Args:
        report_type (str): Report type string.
        format (str): File format extension string.
        date (Optional[str]): Target date query parameter.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        Response: Binary file response with attachment disposition.
    """
    try:
        logging.info(f"Calling GET /reports/export endpoint | Type: {report_type} | Format: {format}")
        content, media_type, filename = await ReportController().export_report(
            report_type=report_type,
            format_type=format,
            target_date=date,
            current_user=current_user,
        )
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return Response(content=content, media_type=media_type, headers=headers)
    except HTTPException as httperror:
        logging.error(f"Error in GET /reports/export endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /reports/export endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
