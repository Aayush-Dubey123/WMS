"""
idempotency_service.py — Service enforcing idempotency key locks.

Prevents duplicate execution of scanning and mutation requests using Idempotency-Key headers.
"""

from datetime import datetime

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from pytz import timezone

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


class IdempotencyService:
    """Service facade enforcing idempotent request execution."""

    async def lock_key(self, key: str, endpoint: str, actor_id: str) -> bool:
        """
        Attempt to claim and store an idempotency key.

        Args:
            key (str): Idempotency key string from request header.
            endpoint (str): Endpoint path executing request.
            actor_id (str): ID of user executing request.

        Returns:
            bool: True if key claim was successful.

        Raises:
            HTTPException 409: If idempotency key was already claimed (duplicate request).
        """
        try:
            logging.info(f"Executing IdempotencyService.lock_key for key: {key}")
            db = MongoDatabase()
            doc = {
                "key": key.strip(),
                "endpoint": endpoint,
                "actor_id": actor_id,
                "timestamp": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
            await db.idempotency_keys.insert_one(doc)
            logging.info(f"Idempotency key locked successfully: {key}")
            return True
        except DuplicateKeyError:
            logging.warning(f"Idempotency conflict: key {key} already processed")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate request detected for idempotency key '{key}'. Request already processed.",
            )
        except Exception as error:
            logging.error(f"Error in IdempotencyService.lock_key: {error}")
            raise


_idempotency_service_instance: IdempotencyService | None = None


def get_idempotency_service() -> IdempotencyService:
    """
    Retrieve global IdempotencyService instance.

    Returns:
        IdempotencyService: Shared idempotency service instance.
    """
    global _idempotency_service_instance
    if _idempotency_service_instance is None:
        _idempotency_service_instance = IdempotencyService()
    return _idempotency_service_instance
