"""
audit_response.py — Response schemas for audit log endpoints.

Defines AuditLogResponse and AuditLogListResponse models.
"""

from typing import Any

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Response payload representing audit log record."""

    id: str = Field(..., description="Audit log entry unique ID")
    actor_id: str = Field(..., description="Actor user ID")
    actor_email: str | None = Field(default=None, description="Actor email address")
    actor_role: str = Field(..., description="Actor RBAC role")
    action: str = Field(..., description="Mutation action name")
    collection: str = Field(..., description="Target database collection name")
    doc_id: str = Field(..., description="Target document ID string")
    before: dict[str, Any] | None = Field(default=None, description="State before mutation")
    after: dict[str, Any] | None = Field(default=None, description="State after mutation")
    timestamp: str = Field(..., description="UTC mutation timestamp string")


class AuditLogListResponse(BaseModel):
    """Response payload wrapper for querying audit logs."""

    logs: list[AuditLogResponse] = Field(..., description="List of audit log objects")
    total: int = Field(..., description="Total matching audit log record count")
