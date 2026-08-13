"""
query_response.py — Response schema for natural language stock query.

Defines Pydantic response model for POST /query endpoint.
"""

from typing import Any

from pydantic import BaseModel, Field


class NLQueryResponse(BaseModel):
    """Response payload for natural language query execution."""

    template_used: str = Field(..., description="Allow-listed aggregation query template ID")
    description: str = Field(..., description="Description of the template logic applied")
    query_text: str = Field(..., description="Original query prompt string")
    results: list[dict[str, Any]] = Field(..., description="Query result row records")
