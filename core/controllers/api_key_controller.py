"""
api_key_controller.py — Controller for API Key creation, listing, and revocation.

Manages external API key generation, raw secret key output (once only), hashing, and deletion.
"""

import uuid
from datetime import datetime

from fastapi import HTTPException, status
from pytz import timezone

from commons.api_key_auth import hash_api_key
from core import logger
from core.cruds.api_key_crud import CRUDApiKey

logging = logger(__name__)


class ApiKeyController:
    """Controller managing API key administration."""

    def __init__(self):
        """Initialize ApiKeyController with CRUDApiKey."""
        self._key_crud = CRUDApiKey()

    async def create_key(self, key_data: dict, current_user: dict) -> dict:
        """
        Generate a new scoped API key. Returns raw secret key ONLY ONCE.

        Args:
            key_data (dict): Key creation payload.
            current_user (dict): Authenticated user dictionary (OWNER or MANAGER).

        Returns:
            dict: API key response containing raw secret key.
        """
        try:
            logging.info("Executing ApiKeyController.create_key")
            raw_secret = f"wms_live_{uuid.uuid4().hex}"
            prefix = raw_secret[:12]
            key_hash = hash_api_key(raw_secret)

            key_payload = {
                "name": key_data.get("name"),
                "key_hash": key_hash,
                "prefix": prefix,
                "role": key_data.get("role", "STAFF"),
                "scopes": key_data.get("scopes", ["read"]),
                "is_active": True,
                "created_by": current_user["id"],
                "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }

            created = await self._key_crud.create(key_payload)
            created["raw_key"] = raw_secret

            logging.info(f"API key created successfully! Name: {created['name']} | Prefix: {prefix}")
            return created
        except Exception as error:
            logging.error(f"Error in ApiKeyController.create_key: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_keys(self, current_user: dict) -> list[dict]:
        """
        List API keys created by current user.

        Args:
            current_user (dict): Authenticated user dictionary.

        Returns:
            List[dict]: List of API key records (without raw secrets).
        """
        try:
            logging.info("Executing ApiKeyController.list_keys")
            keys = await self._key_crud.list_keys(user_id=current_user["id"])
            return keys
        except Exception as error:
            logging.error(f"Error in ApiKeyController.list_keys: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def revoke_key(self, key_id: str, current_user: dict) -> dict:
        """
        Revoke an API key.

        Args:
            key_id (str): API key ID.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Revoked key record.

        Raises:
            HTTPException 404: Key not found.
        """
        try:
            logging.info(f"Executing ApiKeyController.revoke_key: {key_id}")
            revoked = await self._key_crud.revoke(id=key_id)
            if not revoked:
                logging.warning(f"API key revocation failed: key {key_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="API key not found",
                )
            logging.info(f"API key revoked successfully: {key_id}")
            return revoked
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in ApiKeyController.revoke_key: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
