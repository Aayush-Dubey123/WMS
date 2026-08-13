"""
health_router.py — Health check endpoint routes.

Exposes GET /health and GET /v1/health endpoints for load balancers and system monitoring.
"""

from fastapi import APIRouter, HTTPException, status

from core import logger
from core.apis.schemas.responses.health_response import HealthResponse
from core.controllers.health_controller import HealthController

health_router = APIRouter()
logging = logger(__name__)


@health_router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
    tags=["Health"],
)
@health_router.get(
    "/v1/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
    tags=["Health"],
)
async def get_health():
    """
    Retrieve application health status.

    Verifies API server status and underlying MongoDB database connectivity.

    Returns:
        HealthResponse: Health status information.

    Raises:
        HTTPException 503: Service unavailable if database is disconnected.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling GET /health endpoint")
        response = await HealthController().get_health()
        return HealthResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /health endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /health endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
