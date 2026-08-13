"""
vision_response.py — Response schema for OpenCV vision measurement.

Defines Pydantic response model for POST /vision/measure endpoint.
"""


from pydantic import BaseModel, Field


class VisionMeasureResponse(BaseModel):
    """Response payload for OpenCV vision package dimension measurement."""

    width: float = Field(..., description="Estimated package width in inches")
    height: float = Field(..., description="Estimated package height in inches")
    weight: float = Field(default=0.0, description="Package weight (ALWAYS manual)")
    confidence: float = Field(..., description="Vision detection confidence score (0.0 to 1.0)")
    marker_found: bool = Field(..., description="Whether ArUco reference marker was detected")
    error: str | None = Field(default=None, description="Detection error message if marker missing")
