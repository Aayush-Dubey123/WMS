"""
facility_router.py — Warehouse facility management endpoint routes.

Exposes endpoints for creating, listing, viewing, and updating warehouse facilities.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from commons.auth import require_roles
from core import logger
from core.apis.schemas.requests.facility_request import (
    WarehouseCreateRequest,
    WarehouseUpdateRequest,
)
from core.apis.schemas.responses.facility_response import (
    WarehouseListResponse,
    WarehouseResponse,
)
from core.controllers.facility_controller import WarehouseController

facility_router = APIRouter(prefix="/warehouses", tags=["Warehouses"])
logging = logger(__name__)


@facility_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=WarehouseResponse,
)
async def create_warehouse(
    request: WarehouseCreateRequest,
    current_user: dict = Depends(require_roles(["OWNER"])),
):
    """
    Create a new warehouse facility (Owner only).

    Args:
        request (WarehouseCreateRequest): Warehouse creation parameters.
        current_user (dict): Authenticated user (OWNER role required).

    Returns:
        WarehouseResponse: Created warehouse details.

    Raises:
        HTTPException 400: Duplicate warehouse code.
        HTTPException 403: Forbidden if not Owner.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /warehouses endpoint")
        response = await WarehouseController().create_warehouse(
            wh_data=request.model_dump(),
            current_user=current_user,
        )
        return WarehouseResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /warehouses endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /warehouses endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@facility_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=WarehouseListResponse,
)
async def list_warehouses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    List all warehouse facilities.

    Args:
        skip (int): Pagination offset count.
        limit (int): Maximum records to return.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        WarehouseListResponse: List of warehouse facilities.

    Raises:
        HTTPException 403: Forbidden for Staff.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling GET /warehouses endpoint")
        response = await WarehouseController().list_warehouses(skip=skip, limit=limit)
        return WarehouseListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /warehouses endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /warehouses endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@facility_router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=WarehouseResponse,
)
async def get_warehouse(
    id: str,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Retrieve warehouse facility details by ID.

    Args:
        id (str): Warehouse ID string.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        WarehouseResponse: Warehouse details.

    Raises:
        HTTPException 404: Warehouse not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling GET /warehouses/{id} endpoint")
        response = await WarehouseController().get_warehouse_by_id(wh_id=id)
        return WarehouseResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /warehouses/{id} endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /warehouses/{id} endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@facility_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=WarehouseResponse,
)
async def update_warehouse(
    id: str,
    request: WarehouseUpdateRequest,
    current_user: dict = Depends(require_roles(["OWNER"])),
):
    """
    Update warehouse facility details (Owner only).

    Args:
        id (str): Warehouse ID string.
        request (WarehouseUpdateRequest): Update payload.
        current_user (dict): Authenticated user (OWNER role required).

    Returns:
        WarehouseResponse: Updated warehouse details.

    Raises:
        HTTPException 404: Warehouse not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling PUT /warehouses/{id} endpoint")
        response = await WarehouseController().update_warehouse(
            wh_id=id,
            update_data=request.model_dump(),
            current_user=current_user,
        )
        return WarehouseResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in PUT /warehouses/{id} endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in PUT /warehouses/{id} endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
