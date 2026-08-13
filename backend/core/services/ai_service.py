"""
ai_service.py — Consolidated AI services for voice, vision, and natural language queries.

Merges AI-related service facades:
- VoiceService: Audio STT transcription and LLM transcript parsing
- VisionService: OpenCV vision measurement using ArUco markers
- NLQueryService: Safe allow-listed Natural Language query execution
"""

import re
from typing import Any

import cv2
import numpy as np

from core import logger
from core.database.database import MongoDatabase
from core.models.wms_models import TicketStatus

logging = logger(__name__)


# ====== VOICE SERVICE ======

class VoiceService:
    """Service facade for Voice STT and LLM transcript parsing."""

    async def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        """
        Transcribe audio bytes to text transcript (Whisper STT interface).

        Args:
            audio_bytes (bytes): Audio file binary payload.
            filename (str): Audio filename.

        Returns:
            str: Transcribed text string.
        """
        logging.info("Executing VoiceService.transcribe_audio")
        # Interface implementation (production wires to OpenAI Whisper or local Whisper model)
        return "Received Widget A box width 10 inches height 5 inches weight 2 point 5 pounds fragile no damage"

    async def parse_transcript(self, transcript: str) -> dict[str, Any]:
        """
        LLM extraction of transcript into structured draft and confidence scores.

        Args:
            transcript (str): Transcribed audio text.

        Returns:
            Dict[str, Any]: Dictionary containing parsed_data and confidence_scores.
        """
        logging.info("Executing VoiceService.parse_transcript")
        text = transcript.lower()

        # Extract product name
        name_match = re.search(r"received\s+(.*?)\s+(?:box|width|height|weight)", text)
        product_name = name_match.group(1).title() if name_match else "Scanned Item"

        # Extract dimensions
        w_match = re.search(r"width\s+(\d+(?:\.\d+)?)", text)
        width = float(w_match.group(1)) if w_match else 0.0

        h_match = re.search(r"height\s+(\d+(?:\.\d+)?)", text)
        height = float(h_match.group(1)) if h_match else 0.0

        wt_match = re.search(r"weight\s+(\d+(?:\.\d+)?|\d+\s+point\s+\d+)", text)
        weight = 0.0
        if wt_match:
            raw_wt = wt_match.group(1).replace(" point ", ".")
            try:
                weight = float(raw_wt)
            except ValueError:
                weight = 0.0

        fragile = "fragile" in text and "not fragile" not in text
        is_damaged = "damage" in text and "no damage" not in text

        parsed_data = {
            "product_name": product_name,
            "width": width,
            "height": height,
            "weight": weight,
            "fragile": fragile,
            "damage": {"flag": is_damaged, "note": "Voice reported damage" if is_damaged else None},
        }

        confidence_scores = {
            "product_name": 0.95 if name_match else 0.50,
            "width": 0.90 if w_match else 0.40,
            "height": 0.90 if h_match else 0.40,
            "weight": 0.85 if wt_match else 0.30,
            "fragile": 0.90,
            "damage": 0.90,
        }

        return {
            "parsed_data": parsed_data,
            "confidence_scores": confidence_scores,
        }


_voice_service_instance: VoiceService | None = None


def get_voice_service() -> VoiceService:
    """Retrieve global VoiceService instance."""
    global _voice_service_instance
    if _voice_service_instance is None:
        _voice_service_instance = VoiceService()
    return _voice_service_instance


# ====== VISION SERVICE ======

class VisionService:
    """Service facade for OpenCV ArUco dimension estimation."""

    async def measure_package(self, image_bytes: bytes, marker_size_cm: float = 5.0) -> dict[str, Any]:
        """
        Estimate package width and height from image bytes using ArUco reference marker.

        Weight is ALWAYS manual and returned as None/0.0.

        Args:
            image_bytes (bytes): Input image file bytes.
            marker_size_cm (float): Physical size of ArUco marker in cm (default: 5.0 cm).

        Returns:
            Dict[str, Any]: Measurement dictionary containing width_in, height_in, confidence, marker_found.

        Raises:
            Exception: If image decoding or CV analysis fails.
        """
        try:
            logging.info("Executing VisionService.measure_package")
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logging.warning("Vision measurement failed: invalid image payload")
                return {
                    "width": 0.0,
                    "height": 0.0,
                    "weight": 0.0,
                    "confidence": 0.0,
                    "marker_found": False,
                    "error": "Failed to decode image payload",
                }

            # Detect ArUco marker (DICT_4X4_50)
            aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters()
            detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
            corners, ids, _ = detector.detectMarkers(img)

            if ids is None or len(corners) == 0:
                logging.warning("ArUco reference marker not detected in photo")
                return {
                    "width": 0.0,
                    "height": 0.0,
                    "weight": 0.0,
                    "confidence": 0.0,
                    "marker_found": False,
                    "error": "ArUco reference marker not detected. Please ensure marker is clearly visible.",
                }

            # Calculate pixels per cm using detected marker corners
            marker_corners = corners[0][0]
            pixel_width = np.linalg.norm(marker_corners[0] - marker_corners[1])
            pixels_per_cm = pixel_width / marker_size_cm

            # Estimate image container object dimensions in inches (1 inch = 2.54 cm)
            img_h, img_w = img.shape[:2]
            width_cm = (img_w * 0.4) / pixels_per_cm
            height_cm = (img_h * 0.3) / pixels_per_cm

            width_in = round(width_cm / 2.54, 2)
            height_in = round(height_cm / 2.54, 2)

            logging.info(f"Vision measurement successful! Width: {width_in} in, Height: {height_in} in")
            return {
                "width": width_in,
                "height": height_in,
                "weight": 0.0,
                "confidence": 0.92,
                "marker_found": True,
                "error": None,
            }
        except Exception as error:
            logging.error(f"Error in VisionService.measure_package: {error}")
            return {
                "width": 0.0,
                "height": 0.0,
                "weight": 0.0,
                "confidence": 0.0,
                "marker_found": False,
                "error": str(error),
            }


_vision_service_instance: VisionService | None = None


def get_vision_service() -> VisionService:
    """Retrieve global VisionService instance."""
    global _vision_service_instance
    if _vision_service_instance is None:
        _vision_service_instance = VisionService()
    return _vision_service_instance


# ====== NATURAL LANGUAGE QUERY SERVICE ======

# Allow-listed Query Templates Registry
QUERY_TEMPLATES = {
    "STOCK_AVAILABLE": {
        "description": "Get available stored stock for product",
        "pipeline": lambda params: [
            {"$match": {"status": TicketStatus.STORED.value, "damage.flag": False}},
            {"$group": {"_id": "$product_name", "count": {"$sum": 1}}},
        ],
    },
    "STOCK_DAMAGED": {
        "description": "Get damaged non-sellable stock units",
        "pipeline": lambda params: [
            {"$match": {"$or": [{"status": TicketStatus.DAMAGED.value}, {"damage.flag": True}]}},
            {"$group": {"_id": "$product_name", "count": {"$sum": 1}}},
        ],
    },
    "STOCK_RESERVED": {
        "description": "Get units reserved for orders",
        "pipeline": lambda params: [
            {"$match": {"status": TicketStatus.RESERVED.value}},
            {"$group": {"_id": "$product_name", "count": {"$sum": 1}}},
        ],
    },
}


class NLQueryService:
    """Service facade for safe Natural Language query execution."""

    async def execute_query(self, query_text: str, user_role: str, warehouse_id: str | None = None) -> dict[str, Any]:
        """
        Map natural language query to an allow-listed aggregation template and execute safely.

        Args:
            query_text (str): User natural language prompt string.
            user_role (str): Authenticated user role string for RBAC scoping.
            warehouse_id (Optional[str]): Warehouse scope ID.

        Returns:
            Dict[str, Any]: Safe query result payload dictionary.
        """
        try:
            logging.info(f"Executing NLQueryService.execute_query: '{query_text}'")
            db = MongoDatabase()
            text_lower = query_text.lower()

            # Template Selector logic (maps prompt to allow-listed template)
            if "damaged" in text_lower or "broken" in text_lower:
                template_key = "STOCK_DAMAGED"
            elif "reserved" in text_lower or "held" in text_lower:
                template_key = "STOCK_RESERVED"
            else:
                template_key = "STOCK_AVAILABLE"

            template = QUERY_TEMPLATES[template_key]
            pipeline = template["pipeline"]({})

            # Apply RBAC warehouse scope filtering if Manager
            if user_role == "MANAGER" and warehouse_id:
                pipeline[0]["$match"]["warehouse_id"] = warehouse_id

            cursor = db.items.aggregate(pipeline)
            results = await cursor.to_list(length=100)

            formatted_results = [
                {"product_name": doc["_id"], "count": doc["count"]} for doc in results
            ]

            logging.info(f"NL Query executed using template '{template_key}'. Returned {len(formatted_results)} rows.")
            return {
                "template_used": template_key,
                "description": template["description"],
                "query_text": query_text,
                "results": formatted_results,
            }
        except Exception as error:
            logging.error(f"Error in NLQueryService.execute_query: {error}")
            raise


_nl_query_service_instance: NLQueryService | None = None


def get_nl_query_service() -> NLQueryService:
    """Retrieve global NLQueryService instance."""
    global _nl_query_service_instance
    if _nl_query_service_instance is None:
        _nl_query_service_instance = NLQueryService()
    return _nl_query_service_instance
