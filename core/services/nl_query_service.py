"""
nl_query_service.py — Safe, allow-listed Natural Language query service.

Maps user natural language stock queries to safe, parameterized MongoDB aggregation templates.
Enforces strict template selection — raw unparsed Mongo queries are NEVER executed.
"""

from typing import Any

from core import logger
from core.database.database import MongoDatabase
from core.models.ticket_model import TicketStatus

logging = logger(__name__)


# Allow-listed Query Templates Registry
QUERY_TEMPLATES = {
    "STOCK_AVAILABLE": {
        "description": "Get available stored stock for product",
        "pipeline": lambda params: [
            {"$match": {"status": TicketStatus.STORED.value, "damage.flag": False}},
            {"$group": {"_id": "$product_name", "count": {"$sum": 1}}},
        ],
    },
    "STOCK_DAMAGED": {
        "description": "Get damaged non-sellable stock units",
        "pipeline": lambda params: [
            {"$match": {"$or": [{"status": TicketStatus.DAMAGED.value}, {"damage.flag": True}]}},
            {"$group": {"_id": "$product_name", "count": {"$sum": 1}}},
        ],
    },
    "STOCK_RESERVED": {
        "description": "Get units reserved for orders",
        "pipeline": lambda params: [
            {"$match": {"status": TicketStatus.RESERVED.value}},
            {"$group": {"_id": "$product_name", "count": {"$sum": 1}}},
        ],
    },
}


class NLQueryService:
    """Service facade for safe Natural Language query execution."""

    async def execute_query(self, query_text: str, user_role: str, warehouse_id: str | None = None) -> dict[str, Any]:
        """
        Map natural language query to an allow-listed aggregation template and execute safely.

        Args:
            query_text (str): User natural language prompt string.
            user_role (str): Authenticated user role string for RBAC scoping.
            warehouse_id (Optional[str]): Warehouse scope ID.

        Returns:
            Dict[str, Any]: Safe query result payload dictionary.
        """
        try:
            logging.info(f"Executing NLQueryService.execute_query: '{query_text}'")
            db = MongoDatabase()
            text_lower = query_text.lower()

            # Template Selector logic (maps prompt to allow-listed template)
            if "damaged" in text_lower or "broken" in text_lower:
                template_key = "STOCK_DAMAGED"
            elif "reserved" in text_lower or "held" in text_lower:
                template_key = "STOCK_RESERVED"
            else:
                template_key = "STOCK_AVAILABLE"

            template = QUERY_TEMPLATES[template_key]
            pipeline = template["pipeline"]({})

            # Apply RBAC warehouse scope filtering if Manager
            if user_role == "MANAGER" and warehouse_id:
                pipeline[0]["$match"]["warehouse_id"] = warehouse_id

            cursor = db.items.aggregate(pipeline)
            results = await cursor.to_list(length=100)

            formatted_results = [
                {"product_name": doc["_id"], "count": doc["count"]} for doc in results
            ]

            logging.info(f"NL Query executed using template '{template_key}'. Returned {len(formatted_results)} rows.")
            return {
                "template_used": template_key,
                "description": template["description"],
                "query_text": query_text,
                "results": formatted_results,
            }
        except Exception as error:
            logging.error(f"Error in NLQueryService.execute_query: {error}")
            raise


_nl_query_service_instance: NLQueryService | None = None


def get_nl_query_service() -> NLQueryService:
    """
    Retrieve global NLQueryService instance.

    Returns:
        NLQueryService: Shared NL query service instance.
    """
    global _nl_query_service_instance
    if _nl_query_service_instance is None:
        _nl_query_service_instance = NLQueryService()
    return _nl_query_service_instance
