"""
user_controller.py — Controller for user account management workflows.

Enforces Owner -> Manager -> Staff administrative creation chain,
warehouse scoping, staff experience assignment, and audit mutation logging.
"""

from datetime import datetime

from fastapi import HTTPException, status
from pytz import timezone

from commons.auth import hash_password
from core import logger
from core.cruds.facility_crud import CRUDWarehouse
from core.cruds.user_crud import CRUDUser
from core.models.user_model import UserRole, UserStatus
from core.services.audit_service import get_audit_service

logging = logger(__name__)


class UserController:
    """Controller managing user account lifecycle and role assignment."""

    def __init__(self):
        """Initialize UserController with CRUDUser, CRUDWarehouse, and AuditService."""
        self._user_crud = CRUDUser()
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

    async def create_manager(self, manager_data: dict, current_user: dict) -> dict:
        """
        Create a new Manager user account (Owner only).

        Args:
            manager_data (dict): Manager creation payload.
            current_user (dict): Authenticated user dictionary (OWNER).

        Returns:
            dict: Created Manager user dictionary.

        Raises:
            HTTPException 400: If email is already registered or warehouse ID is invalid.
            HTTPException 404: If target warehouse facility does not exist.
        """
        try:
            logging.info("Executing UserController.create_manager")
            email = manager_data.get("email", "").lower().strip()
            existing = await self._user_crud.get_by_email(email=email)
            if existing:
                logging.warning(f"Manager creation rejected: email {email} already registered")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{email}' already exists",
                )

            wh_id = manager_data.get("warehouse_id")
            warehouse = await self._wh_crud.get_by_id(id=wh_id)
            if not warehouse:
                logging.warning(f"Manager creation rejected: warehouse {wh_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Warehouse ID '{wh_id}' does not exist",
                )

            user_payload = {
                "email": email,
                "full_name": manager_data.get("full_name"),
                "hashed_password": hash_password(manager_data.get("password")),
                "role": UserRole.MANAGER.value,
                "warehouse_id": wh_id,
                "experience_tier": None,
                "function_roles": [],
                "status": UserStatus.ACTIVE.value,
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_manager = await self._user_crud.create(user_payload)
            # Update warehouse manager reference if unassigned
            await self._wh_crud.update(id=wh_id, update_in={"manager_id": created_manager["id"]})

            await self._audit_service.log_mutation(
                actor=current_user,
                action="CREATE",
                collection="users",
                doc_id=created_manager["id"],
                before=None,
                after=created_manager,
            )
            logging.info(f"Manager user created successfully: {email}")
            return created_manager
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in UserController.create_manager: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def create_staff(self, staff_data: dict, current_user: dict) -> dict:
        """
        Create a new Staff user account (Manager only).

        Automatically scopes staff member to manager's assigned warehouse.

        Args:
            staff_data (dict): Staff creation payload.
            current_user (dict): Authenticated manager user dictionary.

        Returns:
            dict: Created Staff user dictionary.

        Raises:
            HTTPException 400: If email already exists or manager has no warehouse assigned.
        """
        try:
            logging.info("Executing UserController.create_staff")
            email = staff_data.get("email", "").lower().strip()
            existing = await self._user_crud.get_by_email(email=email)
            if existing:
                logging.warning(f"Staff creation rejected: email {email} already registered")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{email}' already exists",
                )

            manager_wh_id = current_user.get("warehouse_id")
            if not manager_wh_id:
                logging.warning(f"Staff creation blocked: Manager {current_user.get('email')} has no assigned warehouse")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Manager account has no assigned warehouse",
                )

            user_payload = {
                "email": email,
                "full_name": staff_data.get("full_name"),
                "hashed_password": hash_password(staff_data.get("password")),
                "role": UserRole.STAFF.value,
                "warehouse_id": manager_wh_id,
                "experience_tier": staff_data.get("experience_tier", "ROOKIE"),
                "function_roles": staff_data.get("function_roles", []),
                "status": UserStatus.ACTIVE.value,
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_staff = await self._user_crud.create(user_payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="CREATE",
                collection="users",
                doc_id=created_staff["id"],
                before=None,
                after=created_staff,
            )
            logging.info(f"Staff user created successfully: {email} for WH: {manager_wh_id}")
            return created_staff
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in UserController.create_staff: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_users(self, current_user: dict, role: str | None = None, skip: int = 0, limit: int = 100) -> dict:
        """
        List users subject to RBAC and warehouse scoping.

        Owner lists across all warehouses; Manager lists only within own warehouse.

        Args:
            current_user (dict): Authenticated user dictionary.
            role (Optional[str]): Optional role filter string.
            skip (int): Pagination offset count.
            limit (int): Maximum records to return.

        Returns:
            dict: Dictionary with list of user dictionaries and total count.
        """
        try:
            logging.info("Executing UserController.list_users")
            filter_query = {}
            if current_user.get("role") == UserRole.MANAGER.value:
                filter_query["warehouse_id"] = current_user.get("warehouse_id")

            if role:
                filter_query["role"] = role

            users, total = await self._user_crud.list_users(filter_query=filter_query, skip=skip, limit=limit)
            return {"users": users, "total": total}
        except Exception as error:
            logging.error(f"Error in UserController.list_users: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def update_staff(self, staff_id: str, update_data: dict, current_user: dict) -> dict:
        """
        Update staff member details (tier, function roles, full name).

        Args:
            staff_id (str): Staff user ID string.
            update_data (dict): Dictionary of update parameters.
            current_user (dict): Authenticated Manager user dictionary.

        Returns:
            dict: Updated staff user dictionary.

        Raises:
            HTTPException 404: If staff user not found.
            HTTPException 403: If manager tries to update staff outside assigned warehouse.
        """
        try:
            logging.info(f"Executing UserController.update_staff for ID: {staff_id}")
            staff_user = await self._user_crud.get_by_id(id=staff_id)
            if not staff_user or staff_user.get("role") != UserRole.STAFF.value:
                logging.warning(f"Staff update failed: user {staff_id} not found or not staff")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Staff user account not found",
                )

            if current_user.get("role") == UserRole.MANAGER.value and staff_user.get("warehouse_id") != current_user.get("warehouse_id"):
                logging.warning(f"Manager {current_user.get('email')} denied cross-warehouse staff update")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot update staff assigned to another warehouse",
                )

            clean_updates = {k: v for k, v in update_data.items() if v is not None}
            clean_updates["updated_at"] = datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f")

            updated_staff = await self._user_crud.update(id=staff_id, update_in=clean_updates)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="UPDATE",
                collection="users",
                doc_id=staff_id,
                before=staff_user,
                after=updated_staff,
            )
            logging.info(f"Staff user updated successfully: {staff_id}")
            return updated_staff
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in UserController.update_staff: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def deactivate_user(self, target_user_id: str, current_user: dict, reassign_to_manager_id: str | None = None) -> dict:
        """
        Deactivate a user account (soft delete).

        Deactivating a Manager requires reassigning their staff members or verifying no staff remain.

        Args:
            target_user_id (str): Target user ID to deactivate.
            current_user (dict): Authenticated user dictionary (OWNER or MANAGER).
            reassign_to_manager_id (Optional[str]): Target manager ID for staff reassignment.

        Returns:
            dict: Deactivated user dictionary.

        Raises:
            HTTPException 400: If deactivating manager without reassigning active staff.
            HTTPException 404: If target user not found.
            HTTPException 403: If manager tries to deactivate user outside their warehouse or non-staff.
        """
        try:
            logging.info(f"Executing UserController.deactivate_user for ID: {target_user_id}")
            target_user = await self._user_crud.get_by_id(id=target_user_id)
            if not target_user:
                logging.warning(f"Deactivation failed: user not found ({target_user_id})")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target user account not found",
                )

            current_role = current_user.get("role")
            if current_role == UserRole.MANAGER.value:
                if target_user.get("role") != UserRole.STAFF.value or target_user.get("warehouse_id") != current_user.get("warehouse_id"):
                    logging.warning(f"Manager {current_user.get('email')} denied deactivation of target user {target_user_id}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Managers can only deactivate staff within their own warehouse",
                    )

            # Owner deactivating Manager check: reassign staff if any exist in manager's warehouse
            if target_user.get("role") == UserRole.MANAGER.value:
                wh_id = target_user.get("warehouse_id")
                if wh_id:
                    staff_in_wh = await self._user_crud.get_by_warehouse(warehouse_id=wh_id, role=UserRole.STAFF.value)
                    active_staff = [s for s in staff_in_wh if s.get("status") == UserStatus.ACTIVE.value]
                    if active_staff:
                        if not reassign_to_manager_id:
                            logging.warning(f"Manager deactivation blocked: active staff exist in WH {wh_id} without reassignment target")
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Deactivating manager requires reassigning {len(active_staff)} active staff. Please provide reassign_to_manager_id.",
                            )
                        reassign_mgr = await self._user_crud.get_by_id(id=reassign_to_manager_id)
                        if not reassign_mgr or reassign_mgr.get("role") != UserRole.MANAGER.value:
                            logging.warning(f"Invalid reassignment manager ID: {reassign_to_manager_id}")
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid target manager for staff reassignment",
                            )

            deactivated_user = await self._user_crud.update(
                id=target_user_id,
                update_in={
                    "status": UserStatus.INACTIVE.value,
                    "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            )
            await self._audit_service.log_mutation(
                actor=current_user,
                action="DEACTIVATE",
                collection="users",
                doc_id=target_user_id,
                before=target_user,
                after=deactivated_user,
            )
            logging.info(f"User account deactivated successfully: {target_user_id}")
            return deactivated_user
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in UserController.deactivate_user: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
