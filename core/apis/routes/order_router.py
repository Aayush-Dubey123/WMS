"""
order_router.py — Outbound order fulfillment endpoint routes.

Exposes endpoints for manual order intake, atomic stock reservation, picklist generation,
packing, carrier shipping label generation, shipping, and reservation cancellation.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from commons.auth import get_current_user
from core import logger
from core.apis.schemas.requests.order_request import (
    OrderCreateRequest,
    OrderPackRequest,
)
from core.apis.schemas.responses.order_response import (
    OrderResponse,
    PicklistResponse,
    ShippingLabelResponse,
)
from core.controllers.wms_controller import OrderController

order_router = APIRouter(prefix="/orders", tags=["Orders & Fulfillment"])
logging = logger(__name__)


@order_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponse,
)
async def create_order(
    request: OrderCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Intake a new customer order (status PENDING).

    Args:
        request (OrderCreateRequest): Order intake parameters.
        current_user (dict): Authenticated user dependency.

    Returns:
        OrderResponse: Created order object.

    Raises:
        HTTPException 400: Duplicate order ID.
        HTTPException 404: Warehouse not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /orders endpoint")
        response = await OrderController().create_order(
            order_data=request.model_dump(),
            current_user=current_user,
        )
        return OrderResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /orders endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /orders endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@order_router.post(
    "/{id}/reserve",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponse,
)
async def reserve_order(
    id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Atomically reserve stock for an order inside a MongoDB transaction (STORED -> RESERVED).

    Concurrent reservation attempts for identical units yield HTTP 409 Conflict.

    Args:
        id (str): Target order ID reference string.
        current_user (dict): Authenticated user dependency.

    Returns:
        OrderResponse: Updated reserved order object.

    Raises:
        HTTPException 400: Insufficient available stock.
        HTTPException 404: Order not found.
        HTTPException 409: Concurrent reservation conflict.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /orders/{id}/reserve endpoint")
        response = await OrderController().reserve_order(
            order_id=id,
            current_user=current_user,
        )
        return OrderResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /orders/{id}/reserve endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /orders/{id}/reserve endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@order_router.get(
    "/{id}/picklist",
    status_code=status.HTTP_200_OK,
    response_model=PicklistResponse,
)
async def get_picklist(
    id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate picklist showing physical bin storage locations for reserved order units.

    Args:
        id (str): Order ID string.
        current_user (dict): Authenticated user dependency.

    Returns:
        PicklistResponse: Picklist object containing item storage location codes.

    Raises:
        HTTPException 404: Order not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling GET /orders/{id}/picklist endpoint")
        response = await OrderController().get_picklist(
            order_id=id,
            current_user=current_user,
        )
        return PicklistResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /orders/{id}/picklist endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /orders/{id}/picklist endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@order_router.post(
    "/{id}/pack",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponse,
)
async def pack_order(
    id: str,
    request: OrderPackRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Confirm packed order weight and package dimensions (transitions status to PACKED).

    Args:
        id (str): Order ID string.
        request (OrderPackRequest): Packing parameters.
        current_user (dict): Authenticated user dependency.

    Returns:
        OrderResponse: Updated packed order object.

    Raises:
        HTTPException 404: Order not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /orders/{id}/pack endpoint")
        response = await OrderController().pack_order(
            order_id=id,
            pack_data=request.model_dump(),
            current_user=current_user,
        )
        return OrderResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /orders/{id}/pack endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /orders/{id}/pack endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@order_router.post(
    "/{id}/label",
    status_code=status.HTTP_200_OK,
    response_model=ShippingLabelResponse,
)
async def generate_label(
    id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate stub carrier shipping label and tracking number.

    Args:
        id (str): Order ID string.
        current_user (dict): Authenticated user dependency.

    Returns:
        ShippingLabelResponse: Shipping label URL and tracking number.

    Raises:
        HTTPException 404: Order not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /orders/{id}/label endpoint")
        response = await OrderController().generate_label(
            order_id=id,
            current_user=current_user,
        )
        return ShippingLabelResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /orders/{id}/label endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /orders/{id}/label endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@order_router.post(
    "/{id}/ship",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponse,
)
async def ship_order(
    id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Ship customer order and transition reserved item units to SOLD state.

    Args:
        id (str): Order ID string.
        current_user (dict): Authenticated user dependency.

    Returns:
        OrderResponse: Updated shipped order object.

    Raises:
        HTTPException 404: Order not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /orders/{id}/ship endpoint")
        response = await OrderController().ship_order(
            order_id=id,
            current_user=current_user,
        )
        return OrderResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /orders/{id}/ship endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /orders/{id}/ship endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@order_router.post(
    "/{id}/cancel",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponse,
)
async def cancel_order(
    id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Cancel order reservation and release items back to STORED status.

    Args:
        id (str): Order ID string.
        current_user (dict): Authenticated user dependency.

    Returns:
        OrderResponse: Updated cancelled order object.

    Raises:
        HTTPException 404: Order not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling POST /orders/{id}/cancel endpoint")
        response = await OrderController().cancel_order(
            order_id=id,
            current_user=current_user,
        )
        return OrderResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /orders/{id}/cancel endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /orders/{id}/cancel endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
