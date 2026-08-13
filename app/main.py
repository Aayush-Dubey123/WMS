"""
app/main.py — Main application entry point for uvicorn app.main:app --reload.

Exports FastAPI app instance from core.apis.api.
"""

from core.apis.api import app as app
