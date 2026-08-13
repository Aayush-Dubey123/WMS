"""
warehouse_controller.py — Controller for warehouse facility operations.

Manages warehouse creation, listing, updating, and audit mutation logging.
"""

from datetime import datetime

from fastapi import HTTPException, status
from pytz import timezone

from core import logger
from core.cruds.warehouse_crud import CRUDWarehouse
from core.services.audit_service import get_audit_service

logging = logger(__name__)


class WarehouseController:
    """Controller managing warehouse facilities."""

    def __init__(self):
        """Initialize WarehouseController with CRUD warehouse and audit service."""
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

    async def create_warehouse(self, wh_data: dict, current_user: dict) -> dict:
        """
        Create a new warehouse facility (Owner only).

        Args:
            wh_data (dict): Warehouse creation payload dictionary.
            current_user (dict): Authenticated user dictionary (must be OWNER).

        Returns:
            dict: Created warehouse record dictionary.

        Raises:
            HTTPException 400: If warehouse code already exists.
            HTTPException 500: Internal server error.
        """
        try:
            logging.info("Executing WarehouseController.create_warehouse")
            code = wh_data.get("code", "").strip().upper()
            existing = await self._wh_crud.get_by_code(code=code)
            if existing:
                logging.warning(f"Warehouse creation rejected: code {code} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Warehouse code '{code}' already exists",
                )

            wh_payload = {
                "code": code,
                "name": wh_data.get("name"),
                "address": wh_data.get("address"),
                "manager_id": None,
                "is_active": True,
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_wh = await self._wh_crud.create(wh_payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="CREATE",
                collection="warehouses",
                doc_id=created_wh["id"],
                before=None,
                after=created_wh,
            )
            logging.info(f"Warehouse created successfully: {code}")
            return created_wh
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in WarehouseController.create_warehouse: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_warehouses(self, skip: int = 0, limit: int = 100) -> dict:
        """
        List warehouse facilities with pagination.

        Args:
            skip (int): Offset skip count.
            limit (int): Maximum items to return.

        Returns:
            dict: Dictionary with list of warehouses and total count.
        """
        try:
            logging.info("Executing WarehouseController.list_warehouses")
            warehouses, total = await self._wh_crud.list_warehouses(skip=skip, limit=limit)
            return {"warehouses": warehouses, "total": total}
        except Exception as error:
            logging.error(f"Error in WarehouseController.list_warehouses: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def get_warehouse_by_id(self, wh_id: str) -> dict:
        """
        Retrieve warehouse details by unique ID.

        Args:
            wh_id (str): Warehouse ID string.

        Returns:
            dict: Warehouse details payload.

        Raises:
            HTTPException 404: If warehouse is not found.
        """
        try:
            logging.info(f"Executing WarehouseController.get_warehouse_by_id: {wh_id}")
            wh = await self._wh_crud.get_by_id(id=wh_id)
            if not wh:
                logging.warning(f"Warehouse not found: {wh_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse facility not found",
                )
            return wh
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in WarehouseController.get_warehouse_by_id: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def update_warehouse(self, wh_id: str, update_data: dict, current_user: dict) -> dict:
        """
        Update warehouse facility parameters (Owner only).

        Args:
            wh_id (str): Warehouse ID string.
            update_data (dict): Dictionary of parameters to update.
            current_user (dict): Authenticated user dictionary (OWNER).

        Returns:
            dict: Updated warehouse dictionary.

        Raises:
            HTTPException 404: If warehouse not found.
        """
        try:
            logging.info(f"Executing WarehouseController.update_warehouse: {wh_id}")
            before = await self._wh_crud.get_by_id(id=wh_id)
            if not before:
                logging.warning(f"Warehouse not found for update: {wh_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse facility not found",
                )

            clean_updates = {k: v for k, v in update_data.items() if v is not None}
            clean_updates["updated_at"] = datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f")

            updated_wh = await self._wh_crud.update(id=wh_id, update_in=clean_updates)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="UPDATE",
                collection="warehouses",
                doc_id=wh_id,
                before=before,
                after=updated_wh,
            )
            logging.info(f"Warehouse updated successfully: {wh_id}")
            return updated_wh
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in WarehouseController.update_warehouse: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
