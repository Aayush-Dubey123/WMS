"""
api_key_auth.py — Authentication dependency for API Key access.

Validates X-API-Key headers against stored hashed API keys.
"""

import hashlib
from typing import Any

from fastapi import Header, HTTPException, status

from core import logger
from core.cruds.api_key_crud import CRUDApiKey

logging = logger(__name__)


def hash_api_key(raw_key: str) -> str:
    """
    Hash raw API key string using SHA256.

    Args:
        raw_key (str): Raw API key string.

    Returns:
        str: Hashed key string.
    """
    return hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()


async def get_api_key_user(x_api_key: str | None = Header(None, alias="X-API-Key")) -> dict[str, Any]:
    """
    FastAPI dependency validating API Key header.

    Args:
        x_api_key (Optional[str]): X-API-Key header value.

    Returns:
        Dict[str, Any]: API key context dictionary containing key metadata and role.

    Raises:
        HTTPException 401: Invalid or missing API key.
    """
    logging.info("Executing get_api_key_user dependency")
    if not x_api_key:
        logging.warning("API key dependency check failed: missing X-API-Key header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header 'X-API-Key' is missing",
        )

    key_hash = hash_api_key(x_api_key)
    key_doc = await CRUDApiKey().get_by_hash(key_hash=key_hash)
    if not key_doc:
        logging.warning("API key dependency check failed: invalid or revoked API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )

    return {
        "id": key_doc["created_by"],
        "email": f"api_key:{key_doc['prefix']}",
        "role": key_doc["role"],
        "scopes": key_doc.get("scopes", ["read"]),
        "is_api_key": True,
        "status": "ACTIVE",
    }
