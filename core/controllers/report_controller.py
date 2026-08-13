"""
report_controller.py — Controller for reporting, stock aggregations, and file exports.

Executes MongoDB aggregation pipelines for executive summary metrics, stock totals,
detail feeds, and downloadable file generation (CSV / XLSX).
"""

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from pytz import timezone

from core import logger
from core.database.database import MongoDatabase
from core.models.ticket_model import TicketStatus
from core.services.export_service import get_export_service

logging = logger(__name__)


class ReportController:
    """Controller managing reporting, stock totals aggregations, and exports."""

    def __init__(self):
        """Initialize ReportController with ExportService."""
        self._export_service = get_export_service()

    async def get_summary(self, target_date: str | None, current_user: dict) -> dict:
        """
        Generate executive summary metrics for a given date (defaults to today UTC).

        Calculates today's tickets, today's sold items, and unannounced arrivals per warehouse.

        Args:
            target_date (Optional[str]): Date string in YYYY-MM-DD format.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Summary metrics payload dictionary.
        """
        try:
            logging.info(f"Executing ReportController.get_summary for date: {target_date}")
            db = MongoDatabase()

            date_prefix = target_date.strip() if target_date else datetime.now(timezone("UTC")).strftime("%Y-%m-%d")

            # Match tickets created on target date
            ticket_cursor = db.tickets.find({"created_at": {"$regex": f"^{date_prefix}"}})
            tickets_today = await ticket_cursor.to_list(length=10000)

            # Match items sold on target date
            item_cursor = db.items.find({"status": TicketStatus.SOLD.value, "updated_at": {"$regex": f"^{date_prefix}"}})
            items_sold_today = await item_cursor.to_list(length=10000)

            total_tickets = len(tickets_today)
            total_sold = len(items_sold_today)
            total_missed = sum(1 for t in tickets_today if t.get("no_ticket_arrival", False))

            # Group per warehouse
            wh_map: dict[str, dict[str, int]] = {}
            for t in tickets_today:
                wh_id = t.get("warehouse_id", "UNKNOWN")
                if wh_id not in wh_map:
                    wh_map[wh_id] = {"todays_tickets": 0, "todays_sold": 0, "arrived_missed": 0}
                wh_map[wh_id]["todays_tickets"] += 1
                if t.get("no_ticket_arrival", False):
                    wh_map[wh_id]["arrived_missed"] += 1

            for item in items_sold_today:
                wh_id = item.get("warehouse_id", "UNKNOWN")
                if wh_id not in wh_map:
                    wh_map[wh_id] = {"todays_tickets": 0, "todays_sold": 0, "arrived_missed": 0}
                wh_map[wh_id]["todays_sold"] += 1

            per_warehouse_list = [
                {
                    "warehouse_id": wh_id,
                    "todays_tickets": metrics["todays_tickets"],
                    "todays_sold": metrics["todays_sold"],
                    "arrived_missed": metrics["arrived_missed"],
                }
                for wh_id, metrics in wh_map.items()
            ]

            return {
                "date": date_prefix,
                "todays_tickets": total_tickets,
                "todays_sold": total_sold,
                "arrived_missed": total_missed,
                "per_warehouse": per_warehouse_list,
            }
        except Exception as error:
            logging.error(f"Error in ReportController.get_summary: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_arrived_today(self, target_date: str | None, current_user: dict, warehouse_id: str | None = None) -> dict:
        """
        Generate detail feed of parcels/tickets arrived on target date.

        Args:
            target_date (Optional[str]): Date string (YYYY-MM-DD).
            current_user (dict): Authenticated user dictionary.
            warehouse_id (Optional[str]): Optional warehouse ID filter.

        Returns:
            dict: Detail feed records dictionary.
        """
        try:
            logging.info("Executing ReportController.get_arrived_today")
            db = MongoDatabase()
            date_prefix = target_date.strip() if target_date else datetime.now(timezone("UTC")).strftime("%Y-%m-%d")

            filter_query: dict[str, Any] = {"created_at": {"$regex": f"^{date_prefix}"}}
            if warehouse_id:
                filter_query["warehouse_id"] = warehouse_id
            elif current_user.get("role") == "MANAGER" and current_user.get("warehouse_id"):
                filter_query["warehouse_id"] = current_user.get("warehouse_id")

            cursor = db.tickets.find(filter_query).sort("created_at", -1)
            tickets = await cursor.to_list(length=10000)

            records = [
                {
                    "ticket_id": t.get("ticket_id"),
                    "warehouse_id": t.get("warehouse_id"),
                    "tracking_number": t.get("tracking_number"),
                    "no_ticket_arrival": t.get("no_ticket_arrival"),
                    "status": t.get("status"),
                    "arrived_by": t.get("arrived_by"),
                    "created_at": t.get("created_at"),
                }
                for t in tickets
            ]

            return {
                "feed_type": "arrived_today",
                "records": records,
                "total": len(records),
            }
        except Exception as error:
            logging.error(f"Error in ReportController.get_arrived_today: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_sold_today(self, target_date: str | None, current_user: dict, warehouse_id: str | None = None) -> dict:
        """
        Generate detail feed of item units sold on target date.

        Args:
            target_date (Optional[str]): Date string (YYYY-MM-DD).
            current_user (dict): Authenticated user dictionary.
            warehouse_id (Optional[str]): Optional warehouse ID filter.

        Returns:
            dict: Detail feed records dictionary.
        """
        try:
            logging.info("Executing ReportController.get_sold_today")
            db = MongoDatabase()
            date_prefix = target_date.strip() if target_date else datetime.now(timezone("UTC")).strftime("%Y-%m-%d")

            filter_query: dict[str, Any] = {
                "status": TicketStatus.SOLD.value,
                "updated_at": {"$regex": f"^{date_prefix}"},
            }
            if warehouse_id:
                filter_query["warehouse_id"] = warehouse_id
            elif current_user.get("role") == "MANAGER" and current_user.get("warehouse_id"):
                filter_query["warehouse_id"] = current_user.get("warehouse_id")

            cursor = db.items.find(filter_query).sort("updated_at", -1)
            items = await cursor.to_list(length=10000)

            records = [
                {
                    "item_id": str(i.get("_id")),
                    "ticket_id": i.get("ticket_id"),
                    "unit_seq": i.get("unit_seq"),
                    "barcode": i.get("barcode"),
                    "product_name": i.get("product_name"),
                    "warehouse_id": i.get("warehouse_id"),
                    "storage_location": i.get("storage_location"),
                    "order_id": i.get("order_id"),
                    "status": i.get("status"),
                    "updated_at": i.get("updated_at"),
                }
                for i in items
            ]

            return {
                "feed_type": "sold_today",
                "records": records,
                "total": len(records),
            }
        except Exception as error:
            logging.error(f"Error in ReportController.get_sold_today: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_stock_totals(self, current_user: dict, warehouse_id: str | None = None) -> dict:
        """
        Execute MongoDB aggregation pipeline calculating stock totals per product and warehouse.

        Calculates on_hand, available, reserved, and damaged unit counts.

        Args:
            current_user (dict): Authenticated user dictionary.
            warehouse_id (Optional[str]): Optional warehouse ID filter.

        Returns:
            dict: Aggregated stock totals dictionary payload.
        """
        try:
            logging.info("Executing ReportController.get_stock_totals aggregation pipeline")
            db = MongoDatabase()

            match_stage: dict[str, Any] = {}
            if warehouse_id:
                match_stage["warehouse_id"] = warehouse_id
            elif current_user.get("role") == "MANAGER" and current_user.get("warehouse_id"):
                match_stage["warehouse_id"] = current_user.get("warehouse_id")

            pipeline = [
                {"$match": match_stage} if match_stage else {"$match": {}},
                {
                    "$group": {
                        "_id": {
                            "barcode": "$barcode",
                            "product_name": "$product_name",
                            "warehouse_id": "$warehouse_id",
                        },
                        "available": {
                            "$sum": {
                                "$cond": [{"$eq": ["$status", TicketStatus.STORED.value]}, 1, 0]
                            }
                        },
                        "reserved": {
                            "$sum": {
                                "$cond": [{"$eq": ["$status", TicketStatus.RESERVED.value]}, 1, 0]
                            }
                        },
                        "damaged": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$or": [
                                            {"$eq": ["$status", TicketStatus.DAMAGED.value]},
                                            {"$eq": ["$damage.flag", True]},
                                        ]
                                    },
                                    1,
                                    0,
                                ]
                            }
                        },
                    }
                },
                {
                    "$project": {
                        "barcode": "$_id.barcode",
                        "product_name": "$_id.product_name",
                        "warehouse_id": "$_id.warehouse_id",
                        "available": 1,
                        "reserved": 1,
                        "damaged": 1,
                        "on_hand": {"$add": ["$available", "$reserved"]},
                    }
                },
            ]

            cursor = db.items.aggregate(pipeline)
            aggregated = await cursor.to_list(length=10000)

            total_on_hand = sum(item["on_hand"] for item in aggregated)
            total_available = sum(item["available"] for item in aggregated)
            total_reserved = sum(item["reserved"] for item in aggregated)
            total_damaged = sum(item["damaged"] for item in aggregated)

            stock_list = [
                {
                    "barcode": item["barcode"],
                    "product_name": item["product_name"],
                    "warehouse_id": item["warehouse_id"],
                    "on_hand": item["on_hand"],
                    "available": item["available"],
                    "reserved": item["reserved"],
                    "damaged": item["damaged"],
                }
                for item in aggregated
            ]

            return {
                "stock": stock_list,
                "total_on_hand": total_on_hand,
                "total_available": total_available,
                "total_reserved": total_reserved,
                "total_damaged": total_damaged,
            }
        except Exception as error:
            logging.error(f"Error in ReportController.get_stock_totals: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def export_report(
        self,
        report_type: str,
        format_type: str,
        target_date: str | None,
        current_user: dict,
    ) -> tuple[bytes, str, str]:
        """
        Generate export file byte stream (CSV or XLSX) for report feeds.

        Args:
            report_type (str): Type of report (arrived, sold, stock).
            format_type (str): Export file format (csv or xlsx).
            target_date (Optional[str]): Date string (YYYY-MM-DD).
            current_user (dict): Authenticated user dictionary.

        Returns:
            tuple[bytes, str, str]: File bytes stream, media_type string, filename string.

        Raises:
            HTTPException 400: Unsupported report or format type.
        """
        try:
            logging.info(f"Executing ReportController.export_report | Type: {report_type} | Format: {format_type}")
            fmt = format_type.strip().lower()
            if fmt not in ["csv", "xlsx"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid export format. Allowed formats: csv, xlsx",
                )

            records = []
            filename_prefix = report_type.lower()

            if report_type.lower() == "arrived":
                feed = await self.get_arrived_today(target_date=target_date, current_user=current_user)
                records = feed["records"]
            elif report_type.lower() == "sold":
                feed = await self.get_sold_today(target_date=target_date, current_user=current_user)
                records = feed["records"]
            elif report_type.lower() == "stock":
                feed = await self.get_stock_totals(current_user=current_user)
                records = feed["stock"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported report export type '{report_type}'",
                )

            if fmt == "csv":
                content = self._export_service.generate_csv(records)
                media_type = "text/csv"
                filename = f"{filename_prefix}_report.csv"
            else:
                content = self._export_service.generate_xlsx(records, title=report_type)
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                filename = f"{filename_prefix}_report.xlsx"

            return content, media_type, filename
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in ReportController.export_report: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
