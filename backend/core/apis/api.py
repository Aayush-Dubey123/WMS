"""
api.py — FastAPI application aggregator and setup module.

Configures application lifespan, database connection setup, CORS middleware,
global routers, security headers, static file mounts, and OpenAPI schema generation.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from core import logger
from core.apis.routes.wms_router import (
    api_key_router,
    approval_router,
    arrival_router,
    audit_router,
    auth_router,
    facility_router,
    health_router,
    inbox_router,
    order_router,
    query_router,
    report_router,
    storage_router,
    ticket_router,
    user_router,
    vision_router,
    voice_router,
)
from core.apis.routes.chatbot_router import chatbot_router
from core.config.settings import settings
from core.database.database import close_mongo_connection, connect_to_mongo
from core.database.init_db import init_db

logging = logger(__name__)
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown lifespan events.

    Establishes MongoDB connection pool, creates database indexes on startup,
    and closes active connection pools gracefully on application shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logging.info("Executing application startup lifespan")
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        await connect_to_mongo()
        await init_db()
        logging.info("Startup lifespan completed successfully")
    except Exception as error:
        logging.error(f"Startup lifespan initialization error: {error}")
    yield
    logging.info("Executing application shutdown lifespan")
    await close_mongo_connection()
    logging.info("Shutdown lifespan completed successfully")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Whitfield Fulfillment WMS REST API Backend",
    redoc_url="/documentation",
    lifespan=lifespan,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    HTTP middleware attaching standard security response headers.

    Args:
        request (Request): Incoming HTTP request object.
        call_next: Middleware handler callback.

    Returns:
        Response: HTTP response with attached security headers.
    """
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Server"] = "Whitfield-WMS-Server"
    return response


allowed_origins = [
    origin.strip()
    for origin in settings.ALLOWED_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Uploads Directory
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Register Core Feature Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(facility_router)
app.include_router(user_router)
app.include_router(audit_router)
app.include_router(inbox_router)
app.include_router(arrival_router)
app.include_router(ticket_router)
app.include_router(approval_router)
app.include_router(storage_router)
app.include_router(order_router)
app.include_router(report_router)
app.include_router(voice_router)
app.include_router(vision_router)
app.include_router(query_router)
app.include_router(api_key_router)
app.include_router(chatbot_router)


@app.get("/", tags=["Root"])
def root_ping():
    """
    Root ping endpoint.

    Returns:
        dict: Server status confirmation message.
    """
    return {"message": f"Welcome to {settings.APP_NAME} API v{settings.APP_VERSION}"}


def custom_openapi():
    """
    Generate or return cached custom OpenAPI specification schema.

    Returns:
        dict: OpenAPI specification schema dictionary.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Whitfield Fulfillment WMS REST API Documentation",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
