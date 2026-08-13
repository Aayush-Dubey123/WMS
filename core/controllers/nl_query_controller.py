"""
nl_query_controller.py — Controller for natural language stock query execution.

Delegates prompts to NLQueryService for safe, template-matched MongoDB aggregations.
"""

from fastapi import HTTPException, status

from core import logger
from core.services.nl_query_service import get_nl_query_service

logging = logger(__name__)


class NLQueryController:
    """Controller managing natural language stock query requests."""

    def __init__(self):
        """Initialize NLQueryController with NLQueryService."""
        self._query_service = get_nl_query_service()

    async def execute_query(self, query_text: str, current_user: dict) -> dict:
        """
        Execute safe natural language stock query.

        Args:
            query_text (str): Query prompt string.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Formatted query response payload dictionary.
        """
        try:
            logging.info("Executing NLQueryController.execute_query")
            role = current_user.get("role", "STAFF")
            wh_id = current_user.get("warehouse_id")
            result = await self._query_service.execute_query(
                query_text=query_text,
                user_role=role,
                warehouse_id=wh_id,
            )
            return result
        except ValueError as error:
            logging.warning(f"NL query rejected outside allow-list: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            )
        except Exception as error:
            logging.error(f"Error in NLQueryController.execute_query: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
