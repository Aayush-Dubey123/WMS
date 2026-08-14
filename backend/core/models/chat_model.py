"""Chat conversation models for Gemini integration."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single message in a conversation."""

    role: str = Field(..., description="'user' or 'model'")
    text: str = Field(..., description="Message content")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp",
    )
    tokens_used: int = Field(default=0, description="Tokens consumed by this message")


class ChatConversation(BaseModel):
    """Complete conversation with metadata."""

    conversation_id: str = Field(..., description="Unique conversation ID")
    user_id: str = Field(..., description="User ID from auth")
    user_role: str = Field(..., description="STAFF/MANAGER/OWNER")
    warehouse_id: str | None = Field(default=None, description="Warehouse scope, nullable")
    messages: list[ChatMessage] = Field(
        default_factory=list, description="All messages in order"
    )
    total_tokens: int = Field(default=0, description="Total tokens used in conversation")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of creation",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of last update",
    )


class ResponseMetrics(BaseModel):
    """Metrics for a single Gemini response."""

    tokens_input: int = Field(..., description="Input tokens from usage_metadata")
    tokens_output: int = Field(..., description="Output tokens from usage_metadata")
    tokens_total: int = Field(..., description="Sum of input + output tokens")
    tool_calls_made: int = Field(default=0, description="Number of tool invocations")
    response_time_ms: float = Field(..., description="Latency in milliseconds")
