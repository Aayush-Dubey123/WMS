"""
storage_controller.py — Controller for warehouse storage bin location management.

Manages physical bin location creation (Zone, Rack, Bin) and retrieval.
"""

from datetime import datetime

from fastapi import HTTPException, status
from pytz import timezone

from core import logger
from core.cruds.facility_crud import CRUDWarehouse
from core.cruds.storage_crud import CRUDStorageLocation
from core.services.audit_service import get_audit_service

logging = logger(__name__)


class StorageController:
    """Controller managing warehouse storage bin locations."""

    def __init__(self):
        """Initialize StorageController with CRUD storage, CRUD warehouse, and AuditService."""
        self._storage_crud = CRUDStorageLocation()
        self._wh_crud = CRUDWarehouse()
        self._audit_service = get_audit_service()

    async def create_location(self, storage_data: dict, current_user: dict) -> dict:
        """
        Create a physical storage location bin in a warehouse facility.

        Location code is constructed as {ZONE}-{RACK}-{BIN} (e.g. A-04-12).

        Args:
            storage_data (dict): Location creation parameters.
            current_user (dict): Authenticated Manager user dictionary.

        Returns:
            dict: Created storage location payload.

        Raises:
            HTTPException 400: Duplicate location code.
            HTTPException 404: Target warehouse facility not found.
        """
        try:
            logging.info("Executing StorageController.create_location")
            wh_id = storage_data.get("warehouse_id")
            warehouse = await self._wh_crud.get_by_id(id=wh_id)
            if not warehouse:
                logging.warning(f"Storage location creation failed: warehouse {wh_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target warehouse facility not found",
                )

            zone = storage_data.get("zone", "").strip().upper()
            rack = storage_data.get("rack", "").strip().upper()
            bin_code = storage_data.get("bin", "").strip().upper()
            location_code = f"{zone}-{rack}-{bin_code}"

            existing = await self._storage_crud.get_by_code(warehouse_id=wh_id, location_code=location_code)
            if existing:
                logging.warning(f"Storage location creation rejected: location code {location_code} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Storage location code '{location_code}' already exists in warehouse",
                )

            payload = {
                "warehouse_id": wh_id,
                "zone": zone,
                "rack": rack,
                "bin": bin_code,
                "location_code": location_code,
                "is_occupied": False,
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
                "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created_location = await self._storage_crud.create(payload)
            await self._audit_service.log_mutation(
                actor=current_user,
                action="CREATE",
                collection="storage_locations",
                doc_id=created_location["id"],
                before=None,
                after=created_location,
            )
            logging.info(f"Storage location created successfully: {location_code}")
            return created_location
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in StorageController.create_location: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_locations(self, warehouse_id: str, skip: int = 0, limit: int = 100) -> dict:
        """
        List storage locations for a warehouse facility.

        Args:
            warehouse_id (str): Target warehouse facility ID.
            skip (int): Offset count.
            limit (int): Maximum records.

        Returns:
            dict: Dictionary with list of storage locations and total count.
        """
        try:
            logging.info(f"Executing StorageController.list_locations for WH: {warehouse_id}")
            locations, total = await self._storage_crud.list_locations(
                warehouse_id=warehouse_id, skip=skip, limit=limit
            )
            return {"locations": locations, "total": total}
        except Exception as error:
            logging.error(f"Error in StorageController.list_locations: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
