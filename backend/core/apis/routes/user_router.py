"""
user_router.py — User management endpoint routes.

Exposes endpoints for creating managers (Owner only), staff (Manager only),
listing users, updating staff, and deactivating accounts.
"""


from fastapi import APIRouter, Depends, HTTPException, Query, status

from commons.auth import require_roles
from core import logger
from core.apis.schemas.requests.user_request import (
    ManagerCreateRequest,
    ManagerDeactivateRequest,
    StaffCreateRequest,
    StaffUpdateRequest,
)
from core.apis.schemas.responses.user_response import UserListResponse, UserResponse
from core.controllers.user_controller import UserController

user_router = APIRouter(prefix="/users", tags=["Users"])
logging = logger(__name__)


@user_router.post(
    "/managers",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_manager(
    request: ManagerCreateRequest,
    current_user: dict = Depends(require_roles(["OWNER"])),
):
    """
    Create a Manager user account assigned to a warehouse (Owner only).

    Args:
        request (ManagerCreateRequest): Manager account payload.
        current_user (dict): Authenticated user (OWNER role required).

    Returns:
        UserResponse: Created Manager user object.

    Raises:
        HTTPException 400: Email already registered or invalid warehouse.
        HTTPException 403: Forbidden for non-Owners.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /users/managers endpoint")
        response = await UserController().create_manager(
            manager_data=request.model_dump(),
            current_user=current_user,
        )
        return UserResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /users/managers endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /users/managers endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@user_router.post(
    "/staff",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_staff(
    request: StaffCreateRequest,
    current_user: dict = Depends(require_roles(["MANAGER"])),
):
    """
    Create a Staff user account scoped to Manager's warehouse (Manager only).

    Args:
        request (StaffCreateRequest): Staff account payload.
        current_user (dict): Authenticated user (MANAGER role required).

    Returns:
        UserResponse: Created Staff user object.

    Raises:
        HTTPException 400: Email already registered.
        HTTPException 403: Forbidden for non-Managers.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info("Calling POST /users/staff endpoint")
        response = await UserController().create_staff(
            staff_data=request.model_dump(),
            current_user=current_user,
        )
        return UserResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /users/staff endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /users/staff endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@user_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserListResponse,
)
async def list_users(
    role: str | None = Query(None, description="Filter by user role (OWNER, MANAGER, STAFF)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    List user accounts subject to RBAC and warehouse scoping.

    Args:
        role (Optional[str]): Role filter.
        skip (int): Offset count.
        limit (int): Maximum records.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        UserListResponse: List of matching users.
    """
    try:
        logging.info("Calling GET /users endpoint")
        response = await UserController().list_users(
            current_user=current_user,
            role=role,
            skip=skip,
            limit=limit,
        )
        return UserListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /users endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in GET /users endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@user_router.put(
    "/staff/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def update_staff(
    id: str,
    request: StaffUpdateRequest,
    current_user: dict = Depends(require_roles(["MANAGER", "OWNER"])),
):
    """
    Update staff user account properties (experience tier, function roles).

    Args:
        id (str): Staff user ID.
        request (StaffUpdateRequest): Update parameters payload.
        current_user (dict): Authenticated user (MANAGER or OWNER).

    Returns:
        UserResponse: Updated staff object.

    Raises:
        HTTPException 404: Staff user not found.
        HTTPException 403: Cross-warehouse update prohibited.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling PUT /users/staff/{id} endpoint")
        response = await UserController().update_staff(
            staff_id=id,
            update_data=request.model_dump(),
            current_user=current_user,
        )
        return UserResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in PUT /users/staff/{id} endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in PUT /users/staff/{id} endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@user_router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def deactivate_user(
    id: str,
    deactivate_payload: ManagerDeactivateRequest | None = None,
    current_user: dict = Depends(require_roles(["OWNER", "MANAGER"])),
):
    """
    Deactivate a user account (soft delete).

    Deactivating a Manager requires reassigning active staff members using reassign_to_manager_id.

    Args:
        id (str): Target user ID to deactivate.
        deactivate_payload (Optional[ManagerDeactivateRequest]): Optional reassignment payload.
        current_user (dict): Authenticated user (OWNER or MANAGER).

    Returns:
        UserResponse: Deactivated user object.

    Raises:
        HTTPException 400: Active staff exist without reassignment.
        HTTPException 404: User not found.
        HTTPException 500: Internal server error.
    """
    try:
        logging.info(f"Calling DELETE /users/{id} endpoint")
        reassign_id = deactivate_payload.reassign_to_manager_id if deactivate_payload else None
        response = await UserController().deactivate_user(
            target_user_id=id,
            current_user=current_user,
            reassign_to_manager_id=reassign_id,
        )
        return UserResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in DELETE /users/{id} endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in DELETE /users/{id} endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
