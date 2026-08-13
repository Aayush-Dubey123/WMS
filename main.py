"""
main.py — Application entry point.

Run with:
    python main.py
    OR
    uvicorn core.apis.api:app --reload --port 8000

The import here is intentionally minimal — all setup happens inside api.py.
main.py is only the launcher.
"""

import uvicorn

from core.apis.api import app as app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        server_header=False,
    )
