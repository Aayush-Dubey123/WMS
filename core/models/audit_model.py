"""
audit_model.py — Audit log persistence model.

Defines AuditLog document schema stored in MongoDB audit_log collection.
Tracks mutations, actor details, collection targets, and before/after states.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from pytz import timezone


class AuditLog(BaseModel):
    """
    Audit log record persistence schema.

    Records immutable system mutation actions for audit compliance.
    """

    id: str | None = Field(default=None, alias="_id", description="MongoDB ObjectId hex string")
    actor_id: str = Field(..., description="ID of user performing action")
    actor_email: str | None = Field(default=None, description="Email of user performing action")
    actor_role: str = Field(..., description="Role of user performing action")
    action: str = Field(..., description="Mutation action name (e.g. CREATE, UPDATE, DELETE)")
    collection: str = Field(..., description="Target database collection modified")
    doc_id: str = Field(..., description="Target document ID modified")
    before: dict[str, Any] | None = Field(
        default=None, description="Document state before mutation"
    )
    after: dict[str, Any] | None = Field(
        default=None, description="Document state after mutation"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        description="UTC mutation timestamp string",
    )
