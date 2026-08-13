"""
auth.py — Authentication, password hashing, JWT, and RBAC security module.

Provides password hashing/verification using direct bcrypt,
JWT access and refresh token creation and decoding,
and FastAPI security dependencies for role-based access control.
"""

from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pytz import timezone

from core import logger
from core.config.settings import settings

logging = logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password (str): Plain text password string.

    Returns:
        str: Hashed password string.
    """
    logging.info("Executing hash_password function")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed bcrypt password.

    Args:
        plain_password (str): Plain text password input.
        hashed_password (str): Stored hashed bcrypt password.

    Returns:
        bool: True if password matches hash, False otherwise.
    """
    logging.info("Executing verify_password function")
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as error:
        logging.warning(f"Password verification check failed: {error}")
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        data (Dict[str, Any]): Token payload claims.
        expires_delta (Optional[timedelta]): Custom token expiration duration.

    Returns:
        str: Encoded JWT token string.
    """
    logging.info("Executing create_access_token function")
    to_encode = data.copy()
    now = datetime.now(timezone("UTC"))
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a signed JWT refresh token.

    Args:
        data (Dict[str, Any]): Token payload claims.

    Returns:
        str: Encoded JWT refresh token string.
    """
    logging.info("Executing create_refresh_token function")
    to_encode = data.copy()
    expire = datetime.now(timezone("UTC")) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decodeJWT(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a signed JWT token string.

    Args:
        token (str): JWT token string.

    Returns:
        Optional[Dict[str, Any]]: Decoded payload dictionary if valid, None if invalid or expired.
    """
    logging.info("Executing decodeJWT function")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError as error:
        logging.warning(f"Failed to decode JWT token: {error}")
        return None


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict[str, Any]:
    """
    FastAPI dependency resolving current authenticated user from bearer token.

    Args:
        token (Optional[str]): Bearer token extracted from HTTP authorization header.

    Returns:
        Dict[str, Any]: Authenticated user dictionary from database.

    Raises:
        HTTPException 401: If bearer token is missing, invalid, or expired.
        HTTPException 403: If user account is inactive.
    """
    logging.info("Executing get_current_user dependency")
    if not token:
        logging.warning("Missing authentication token in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decodeJWT(token)
    if not payload or payload.get("type") != "access":
        logging.warning("Invalid or expired JWT access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        logging.warning("JWT payload missing subject user ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Deferred import to prevent circular import with CRUDUser
    from core.cruds.user_crud import CRUDUser
    user = await CRUDUser().get_by_id(id=user_id)
    if not user:
        logging.warning(f"Authenticated user not found in database: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
        )

    if user.get("status") != "ACTIVE":
        logging.warning(f"User account is not ACTIVE: {user.get('email')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended",
        )

    return user


def require_roles(allowed_roles: list[str]):
    """
    FastAPI dependency factory enforcing role-based authorization (RBAC).

    Args:
        allowed_roles (List[str]): List of role strings permitted to access route.

    Returns:
        Callable dependency validating user's role.
    """
    async def role_checker(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        logging.info("Executing require_roles dependency check")
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            logging.warning(
                f"User {current_user.get('email')} with role {user_role} denied access. Required: {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker
