"""
query_router.py — Natural Language stock search query route.

Exposes endpoint POST /query.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from commons.auth import get_current_user
from core import logger
from core.apis.schemas.requests.query_request import NLQueryRequest
from core.apis.schemas.responses.query_response import NLQueryResponse
from core.controllers.wms_controller import NLQueryController

query_router = APIRouter(tags=["Natural Language Query"])
logging = logger(__name__)


@query_router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=NLQueryResponse,
)
async def process_nl_query(
    request: NLQueryRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Execute natural language stock search using safe allow-listed query templates.

    Args:
        request (NLQueryRequest): Query prompt request payload.
        current_user (dict): Authenticated user dependency.

    Returns:
        NLQueryResponse: Result payload dictionary.
    """
    try:
        logging.info("Calling POST /query endpoint")
        response = await NLQueryController().execute_query(
            query_text=request.query,
            current_user=current_user,
        )
        return NLQueryResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /query endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /query endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
