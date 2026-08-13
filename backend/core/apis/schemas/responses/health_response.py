"""
health_response.py — Response schema for health check endpoints.

Defines API output contracts for system and database status checks.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """
    Schema for system health check response payload.

    Provides status of the API service, database connectivity, and timestamp.
    """

    status: str = Field(..., description="Overall system health status (ok/error)")
    service: str = Field(..., description="Service identifier name")
    version: str = Field(..., description="Application semantic version")
    database: str = Field(..., description="Database connection status (connected/disconnected)")
    timestamp: str = Field(..., description="UTC ISO timestamp of health check")
