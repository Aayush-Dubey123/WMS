"""
health_controller.py — Controller for system health operations.

Orchestrates database ping checks and formats health status payloads.
"""

from datetime import datetime

from fastapi import HTTPException, status
from pytz import timezone

from core import logger
from core.config.settings import settings
from core.database.database import ping

logging = logger(__name__)


class HealthController:
    """
    Controller managing system and database health validation.

    Coordinates database connection verification and returns structured health details.
    """

    async def get_health(self) -> dict:
        """
        Check database connectivity and generate system health payload.

        Returns:
            dict: Dictionary containing health status, database connection, and timestamp.

        Raises:
            HTTPException: If database ping fails or system is unhealthy.
        """
        try:
            logging.info("Executing HealthController.get_health")
            db_status = "connected"
            try:
                await ping()
            except Exception as db_err:
                logging.warning(f"Database ping failed in HealthController: {db_err}")
                db_status = "disconnected"

            system_ok = db_status == "connected"
            timestamp = datetime.now(timezone("UTC")).isoformat()

            if not system_ok:
                logging.warning("System health status check failed due to database issue")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "status": "degraded",
                        "service": settings.APP_NAME,
                        "version": settings.APP_VERSION,
                        "database": db_status,
                        "timestamp": timestamp,
                    },
                )

            return {
                "status": "ok",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "database": db_status,
                "timestamp": timestamp,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in HealthController.get_health: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
