"""
query_request.py — Request schema for natural language stock query.

Defines Pydantic request model for POST /query endpoint.
"""

from pydantic import BaseModel, Field


class NLQueryRequest(BaseModel):
    """Payload for natural language stock query."""

    query: str = Field(..., min_length=2, description="Natural language search prompt (e.g. 'How many damaged widgets in Reno?')")
