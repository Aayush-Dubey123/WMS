"""
storage_router.py — Physical storage location bin endpoint routes.

Exposes endpoints for creating and listing physical warehouse storage locations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from commons.auth import get_current_user, require_roles
from core import logger
from core.apis.schemas.requests.storage_request import StorageLocationCreateRequest
from core.apis.schemas.responses.storage_response import (
    StorageLocationListResponse,
    StorageLocationResponse,
)
from core.controllers.wms_controller import StorageController

storage_router = APIRouter(prefix="/storage-locations", tags=["Storage Locations"])
logging = logger(__name__)


@storage_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=StorageLocationResponse,
)
async def create_storage_location(
    request: StorageLocationCreateRequest,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Create a new physical storage location bin (Manager/Owner only).

    Constructs combined location_code as {ZONE}-{RACK}-{BIN} (e.g. A-04-12).

    Args:
        request (StorageLocationCreateRequest): Storage location parameters.
        current_user (dict): Authenticated user (MANAGER or OWNER).

    Returns:
        StorageLocationResponse: Created storage location object.

    Raises:
        HTTPException 400: Duplicate location code.
        HTTPException 404: Warehouse not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /storage-locations endpoint")
        response = await StorageController().create_location(
            storage_data=request.model_dump(),
            current_user=current_user,
        )
        return StorageLocationResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /storage-locations endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /storage-locations endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@storage_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=StorageLocationListResponse,
)
async def list_storage_locations(
    warehouse_id: str = Query(..., description="Target warehouse facility ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
):
    """
    List physical storage locations for a warehouse facility.

    Args:
        warehouse_id (str): Warehouse ID query parameter.
        skip (int): Pagination offset.
        limit (int): Maximum records.
        current_user (dict): Authenticated user dependency.

    Returns:
        StorageLocationListResponse: List of storage locations.
    """
    try:
        logging.info(f"Calling GET /storage-locations endpoint for WH: {warehouse_id}")
        response = await StorageController().list_locations(
            warehouse_id=warehouse_id,
            skip=skip,
            limit=limit,
        )
        return StorageLocationListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /storage-locations endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /storage-locations endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
