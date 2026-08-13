"""
vision_controller.py — Controller for OpenCV vision measurement.

Calls VisionService to estimate package dimensions from photo upload with ArUco reference marker.
"""

from fastapi import HTTPException, status

from core import logger
from core.services.vision_service import get_vision_service

logging = logger(__name__)


class VisionController:
    """Controller managing OpenCV vision measurement requests."""

    def __init__(self):
        """Initialize VisionController with VisionService."""
        self._vision_service = get_vision_service()

    async def measure_package(self, image_bytes: bytes, current_user: dict) -> dict:
        """
        Estimate package width and height from uploaded photo containing ArUco reference marker.

        Args:
            image_bytes (bytes): Image binary file content.
            current_user (dict): Authenticated user dictionary.

        Returns:
            dict: Measurement details dictionary.
        """
        try:
            logging.info("Executing VisionController.measure_package")
            result = await self._vision_service.measure_package(image_bytes=image_bytes)
            return result
        except Exception as error:
            logging.error(f"Error in VisionController.measure_package: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
