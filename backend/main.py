"""
main.py — Application entry point.

Run with:
    python main.py
    OR
    uvicorn main:app --reload --port 8000

The import here is intentionally minimal — all setup happens inside api.py.
main.py is only the launcher.
"""
from dotenv import load_dotenv
load_dotenv()   # must run before chatbot_controller is imported

import uvicorn

from core.apis.api import app as app  # noqa: F401 — re-exported for uvicorn main:app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        server_header=False,
    )
