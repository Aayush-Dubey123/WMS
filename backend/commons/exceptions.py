"""
exceptions.py — Centralized application exception definitions and error envelope helpers.

Provides a base WMSException and common HTTP exception factory functions
for consistent error formatting across the WMS API.
"""

from fastapi import HTTPException, status


class WMSException(Exception):
    """
    Base exception class for WMS application errors.

    Wraps all domain-specific errors with a code, message, and optional details.

    Args:
        code (str): Short machine-readable error code (e.g. "WAREHOUSE_NOT_FOUND").
        message (str): Human-readable error description.
        details (dict | None): Optional structured details payload.
    """

    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def not_found(resource: str, resource_id: str = "") -> HTTPException:
    """
    Factory for HTTP 404 Not Found exceptions.

    Args:
        resource (str): Name of the missing resource (e.g. "Warehouse").
        resource_id (str): Optional resource identifier string.

    Returns:
        HTTPException: 404 exception with detail message.
    """
    detail = f"{resource} not found"
    if resource_id:
        detail = f"{resource} '{resource_id}' not found"
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def conflict(message: str) -> HTTPException:
    """
    Factory for HTTP 409 Conflict exceptions.

    Args:
        message (str): Conflict description message.

    Returns:
        HTTPException: 409 exception with detail message.
    """
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def forbidden(message: str = "Access denied") -> HTTPException:
    """
    Factory for HTTP 403 Forbidden exceptions.

    Args:
        message (str): Forbidden reason description.

    Returns:
        HTTPException: 403 exception with detail message.
    """
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def bad_request(message: str) -> HTTPException:
    """
    Factory for HTTP 400 Bad Request exceptions.

    Args:
        message (str): Bad request reason description.

    Returns:
        HTTPException: 400 exception with detail message.
    """
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def internal_error(message: str = "Internal Server Error") -> HTTPException:
    """
    Factory for HTTP 500 Internal Server Error exceptions.

    Args:
        message (str): Error description message.

    Returns:
        HTTPException: 500 exception with detail message.
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
    )
