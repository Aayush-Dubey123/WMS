"""
vision_router.py — OpenCV vision measurement endpoint route.

Exposes endpoint POST /vision/measure.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from commons.auth import get_current_user
from core import logger
from core.apis.schemas.responses.vision_response import VisionMeasureResponse
from core.controllers.wms_controller import VisionController

vision_router = APIRouter(prefix="/vision", tags=["Vision Measurement"])
logging = logger(__name__)


@vision_router.post(
    "/measure",
    status_code=status.HTTP_200_OK,
    response_model=VisionMeasureResponse,
)
async def measure_package(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Estimate package width and height from uploaded photo using ArUco reference marker.

    Args:
        file (UploadFile): Package photo upload binary.
        current_user (dict): Authenticated user dependency.

    Returns:
        VisionMeasureResponse: Estimated package dimensions (weight ALWAYS manual).
    """
    try:
        logging.info("Calling POST /vision/measure endpoint")
        image_bytes = await file.read()
        response = await VisionController().measure_package(
            image_bytes=image_bytes,
            current_user=current_user,
        )
        return VisionMeasureResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /vision/measure endpoint: {httperror}")
        raise
    except Exception as error:
        logging.error(f"Error in POST /vision/measure endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
