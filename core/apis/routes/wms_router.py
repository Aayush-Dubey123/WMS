"""
wms_router.py — Consolidated WMS router aggregator.

Re-exports all 14 WMS feature routers for centralized router registration in api.py:
- api_key_router: API Key administration routes
- approval_router: Ticket approval routes
- arrival_router: Shipment arrival routes
- audit_router: Audit log query routes
- auth_router: User authentication routes
- facility_router: Warehouse facility management routes
- health_router: Health check routes
- inbox_router: Inbox shipment management routes
- order_router: Customer order routes
- query_router: Natural language query routes
- report_router: Report generation routes
- storage_router: Storage location management routes
- ticket_router: Ticket lifecycle routes
- user_router: User management routes
- vision_router: Vision measurement routes
- voice_router: Voice transcription routes

This consolidation simplifies router registration in api.py by importing from
a single module instead of 14 individual route files.
"""

from core.apis.routes.api_key_router import api_key_router
from core.apis.routes.approval_router import approval_router
from core.apis.routes.arrival_router import arrival_router
from core.apis.routes.audit_router import audit_router
from core.apis.routes.auth_router import auth_router
from core.apis.routes.facility_router import facility_router
from core.apis.routes.health_router import health_router
from core.apis.routes.inbox_router import inbox_router
from core.apis.routes.order_router import order_router
from core.apis.routes.query_router import query_router
from core.apis.routes.report_router import report_router
from core.apis.routes.storage_router import storage_router
from core.apis.routes.ticket_router import ticket_router
from core.apis.routes.user_router import user_router
from core.apis.routes.vision_router import vision_router
from core.apis.routes.voice_router import voice_router

__all__ = [
    "api_key_router",
    "approval_router",
    "arrival_router",
    "audit_router",
    "auth_router",
    "facility_router",
    "health_router",
    "inbox_router",
    "order_router",
    "query_router",
    "report_router",
    "storage_router",
    "ticket_router",
    "user_router",
    "vision_router",
    "voice_router",
]
