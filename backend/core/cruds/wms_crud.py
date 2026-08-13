"""
wms_crud.py — Consolidated persistence layer for WMS database operations.

Merges all WMS entity CRUD operations into a single module:
- CRUDApiKey: api_keys collection operations
- CRUDAuditLog: audit_log collection operations
- CRUDWarehouse: warehouses collection operations
- CRUDInbox: inbox_shipments collection operations
- CRUDItem: items collection operations
- CRUDOrder: orders collection operations
- CRUDStorageLocation: storage_locations collection operations
- CRUDTicket: tickets collection operations
- CRUDVoiceDraft: voice_drafts collection operations
"""

from typing import Any

from bson import ObjectId

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


# ====== API KEY CRUD ======

def _format_key_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB API key document into standard schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDApiKey:
    """Database persistence access layer for ApiKey documents."""

    async def create(self, key_in: dict) -> dict:
        """Create a new API key document."""
        try:
            logging.info("Executing CRUDApiKey.create")
            db = MongoDatabase()
            data = dict(key_in)
            result = await db.api_keys.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_key_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDApiKey.create: {error}")
            raise

    async def get_by_hash(self, key_hash: str) -> dict | None:
        """Retrieve active API key document by key hash string."""
        try:
            logging.info("Executing CRUDApiKey.get_by_hash")
            db = MongoDatabase()
            doc = await db.api_keys.find_one({"key_hash": key_hash, "is_active": True})
            return _format_key_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDApiKey.get_by_hash: {error}")
            raise

    async def list_keys(self, user_id: str) -> list[dict]:
        """List all API keys created by user."""
        try:
            logging.info(f"Executing CRUDApiKey.list_keys for user: {user_id}")
            db = MongoDatabase()
            cursor = db.api_keys.find({"created_by": user_id})
            docs = await cursor.to_list(length=100)
            return [_format_key_doc(doc) for doc in docs]
        except Exception as error:
            logging.error(f"Error in CRUDApiKey.list_keys: {error}")
            raise

    async def revoke(self, id: str) -> dict | None:
        """Revoke an API key (sets is_active=False)."""
        try:
            logging.info(f"Executing CRUDApiKey.revoke: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.api_keys.find_one_and_update(
                {"_id": query_id},
                {"$set": {"is_active": False}},
                return_document=True,
            )
            return _format_key_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDApiKey.revoke: {error}")
            raise


# ====== AUDIT LOG CRUD ======

def _format_audit_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB audit document into standard schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDAuditLog:
    """Database persistence access layer for AuditLog documents."""

    async def create(self, audit_in: dict) -> dict:
        """Create a new audit log record in audit_log collection."""
        try:
            logging.info("Executing CRUDAuditLog.create")
            db = MongoDatabase()
            audit_data = dict(audit_in)
            result = await db.audit_log.insert_one(audit_data)
            audit_data["_id"] = result.inserted_id
            return _format_audit_doc(audit_data)
        except Exception as error:
            logging.error(f"Error in CRUDAuditLog.create: {error}")
            raise

    async def list_logs(
        self, filter_query: dict | None = None, skip: int = 0, limit: int = 100
    ) -> tuple[list[dict], int]:
        """Query audit logs with filtering and pagination."""
        try:
            logging.info("Executing CRUDAuditLog.list_logs")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.audit_log.count_documents(query)
            cursor = (
                db.audit_log.find(query)
                .sort("timestamp", -1)
                .skip(skip)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [_format_audit_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDAuditLog.list_logs: {error}")
            raise


# ====== WAREHOUSE/FACILITY CRUD ======

def _format_wh_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB document dictionary into standard warehouse schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDWarehouse:
    """Database persistence access layer for Warehouse documents."""

    async def create(self, wh_in: dict) -> dict:
        """Create a new warehouse document in warehouses collection."""
        try:
            logging.info("Executing CRUDWarehouse.create")
            db = MongoDatabase()
            wh_data = dict(wh_in)
            result = await db.warehouses.insert_one(wh_data)
            wh_data["_id"] = result.inserted_id
            return _format_wh_doc(wh_data)
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """Retrieve warehouse document by unique string ID."""
        try:
            logging.info(f"Executing CRUDWarehouse.get_by_id for ID: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.warehouses.find_one({"_id": query_id})
            return _format_wh_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.get_by_id: {error}")
            raise

    async def get_by_code(self, code: str) -> dict | None:
        """Retrieve warehouse document by unique warehouse short code."""
        try:
            logging.info(f"Executing CRUDWarehouse.get_by_code for code: {code}")
            db = MongoDatabase()
            doc = await db.warehouses.find_one({"code": code.strip().upper()})
            return _format_wh_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.get_by_code: {error}")
            raise

    async def list_warehouses(self, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """List all warehouse facilities with pagination."""
        try:
            logging.info("Executing CRUDWarehouse.list_warehouses")
            db = MongoDatabase()
            total = await db.warehouses.count_documents({})
            cursor = db.warehouses.find({}).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_wh_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.list_warehouses: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """Update warehouse document fields by unique ID."""
        try:
            logging.info(f"Executing CRUDWarehouse.update for ID: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.warehouses.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_wh_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDWarehouse.update: {error}")
            raise


# ====== INBOX SHIPMENT CRUD ======

def _format_inbox_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB document dictionary into standard schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDInbox:
    """Database persistence access layer for InboxShipment documents."""

    async def create(self, inbox_in: dict) -> dict:
        """Create a new inbox shipment record."""
        try:
            logging.info("Executing CRUDInbox.create")
            db = MongoDatabase()
            data = dict(inbox_in)
            result = await db.inbox_shipments.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_inbox_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDInbox.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """Retrieve inbox shipment by unique ID string."""
        try:
            logging.info(f"Executing CRUDInbox.get_by_id: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.inbox_shipments.find_one({"_id": query_id})
            return _format_inbox_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDInbox.get_by_id: {error}")
            raise

    async def get_by_tracking(self, tracking_number: str) -> dict | None:
        """Retrieve accepted inbox shipment by tracking number string."""
        try:
            logging.info(f"Executing CRUDInbox.get_by_tracking: {tracking_number}")
            db = MongoDatabase()
            doc = await db.inbox_shipments.find_one({"tracking_number": tracking_number.strip()})
            return _format_inbox_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDInbox.get_by_tracking: {error}")
            raise

    async def list_shipments(self, filter_query: dict | None = None, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """List inbox shipments with filtering and pagination."""
        try:
            logging.info("Executing CRUDInbox.list_shipments")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.inbox_shipments.count_documents(query)
            cursor = db.inbox_shipments.find(query).sort("created_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_inbox_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDInbox.list_shipments: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """Update inbox shipment fields by unique ID."""
        try:
            logging.info(f"Executing CRUDInbox.update: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.inbox_shipments.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_inbox_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDInbox.update: {error}")
            raise

    async def add_comment(self, id: str, comment_doc: dict) -> dict | None:
        """Push a comment document into inbox shipment comments thread."""
        try:
            logging.info(f"Executing CRUDInbox.add_comment: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.inbox_shipments.find_one_and_update(
                {"_id": query_id},
                {"$push": {"comments": comment_doc}},
                return_document=True,
            )
            return _format_inbox_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDInbox.add_comment: {error}")
            raise


# ====== ITEM CRUD ======

def _format_item_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB item document into standard schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDItem:
    """Database persistence access layer for Item documents."""

    async def create(self, item_in: dict) -> dict:
        """Create a new item document."""
        try:
            logging.info("Executing CRUDItem.create")
            db = MongoDatabase()
            data = dict(item_in)
            result = await db.items.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_item_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDItem.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """Retrieve item by unique string ID."""
        try:
            logging.info(f"Executing CRUDItem.get_by_id: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.items.find_one({"_id": query_id})
            return _format_item_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDItem.get_by_id: {error}")
            raise

    async def get_next_unit_seq(self, ticket_id: str) -> int:
        """Calculate next sequential unit index (1..N) for a given ticket."""
        try:
            logging.info(f"Executing CRUDItem.get_next_unit_seq for ticket: {ticket_id}")
            db = MongoDatabase()
            count = await db.items.count_documents({"ticket_id": ticket_id})
            return count + 1
        except Exception as error:
            logging.error(f"Error in CRUDItem.get_next_unit_seq: {error}")
            raise

    async def get_items_by_ticket(self, ticket_id: str) -> list[dict]:
        """Retrieve all items registered under a ticket_id."""
        try:
            logging.info(f"Executing CRUDItem.get_items_by_ticket: {ticket_id}")
            db = MongoDatabase()
            cursor = db.items.find({"ticket_id": ticket_id}).sort("unit_seq", 1)
            docs = await cursor.to_list(length=1000)
            return [_format_item_doc(doc) for doc in docs]
        except Exception as error:
            logging.error(f"Error in CRUDItem.get_items_by_ticket: {error}")
            raise

    async def update_status_by_ticket(self, ticket_id: str, status_value: str) -> int:
        """Update status for all items attached to a ticket_id (except damaged items)."""
        try:
            logging.info(f"Executing CRUDItem.update_status_by_ticket: {ticket_id} -> {status_value}")
            db = MongoDatabase()
            result = await db.items.update_many(
                {"ticket_id": ticket_id, "damage.flag": False},
                {"$set": {"status": status_value}},
            )
            return result.modified_count
        except Exception as error:
            logging.error(f"Error in CRUDItem.update_status_by_ticket: {error}")
            raise

    async def update_item(self, id: str, update_in: dict) -> dict | None:
        """Update single item document fields by ID."""
        try:
            logging.info(f"Executing CRUDItem.update_item: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.items.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_item_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDItem.update_item: {error}")
            raise


# ====== ORDER CRUD ======

def _format_order_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB order document into standard schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDOrder:
    """Database persistence access layer for Order documents."""

    async def create(self, order_in: dict) -> dict:
        """Create a new order document."""
        try:
            logging.info("Executing CRUDOrder.create")
            db = MongoDatabase()
            data = dict(order_in)
            result = await db.orders.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_order_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDOrder.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """Retrieve order document by unique string ID or order_id string."""
        try:
            logging.info(f"Executing CRUDOrder.get_by_id: {id}")
            db = MongoDatabase()
            filter_doc = {"_id": ObjectId(id)} if ObjectId.is_valid(id) else {"order_id": id}
            doc = await db.orders.find_one(filter_doc)
            return _format_order_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDOrder.get_by_id: {error}")
            raise

    async def get_by_order_id(self, order_id: str) -> dict | None:
        """Retrieve order document by unique order_id code (e.g. ORD-1001)."""
        try:
            logging.info(f"Executing CRUDOrder.get_by_order_id: {order_id}")
            db = MongoDatabase()
            doc = await db.orders.find_one({"order_id": order_id.strip()})
            return _format_order_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDOrder.get_by_order_id: {error}")
            raise

    async def list_orders(self, filter_query: dict | None = None, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """List orders with filtering and pagination."""
        try:
            logging.info("Executing CRUDOrder.list_orders")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.orders.count_documents(query)
            cursor = db.orders.find(query).sort("created_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_order_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDOrder.list_orders: {error}")
            raise

    async def update(self, id: str, update_in: dict, session=None) -> dict | None:
        """Update order fields by unique ID or order_id string, optionally within a session transaction."""
        try:
            logging.info(f"Executing CRUDOrder.update: {id}")
            db = MongoDatabase()
            filter_doc = {"_id": ObjectId(id)} if ObjectId.is_valid(id) else {"order_id": id}
            result = await db.orders.find_one_and_update(
                filter_doc,
                {"$set": update_in},
                return_document=True,
                session=session,
            )
            return _format_order_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDOrder.update: {error}")
            raise


# ====== STORAGE LOCATION CRUD ======

def _format_storage_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB storage location document into standard schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDStorageLocation:
    """Database persistence access layer for StorageLocation documents."""

    async def create(self, storage_in: dict) -> dict:
        """Create a new storage location document."""
        try:
            logging.info("Executing CRUDStorageLocation.create")
            db = MongoDatabase()
            data = dict(storage_in)
            result = await db.storage_locations.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_storage_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDStorageLocation.create: {error}")
            raise

    async def get_by_code(self, warehouse_id: str, location_code: str) -> dict | None:
        """Retrieve storage location document by warehouse ID and location code."""
        try:
            logging.info(f"Executing CRUDStorageLocation.get_by_code: {location_code} in WH {warehouse_id}")
            db = MongoDatabase()
            doc = await db.storage_locations.find_one(
                {"warehouse_id": warehouse_id, "location_code": location_code.strip().upper()}
            )
            return _format_storage_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDStorageLocation.get_by_code: {error}")
            raise

    async def list_locations(self, warehouse_id: str, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """List storage locations for a warehouse."""
        try:
            logging.info(f"Executing CRUDStorageLocation.list_locations for WH: {warehouse_id}")
            db = MongoDatabase()
            query = {"warehouse_id": warehouse_id}
            total = await db.storage_locations.count_documents(query)
            cursor = db.storage_locations.find(query).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_storage_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDStorageLocation.list_locations: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """Update storage location document by ID."""
        try:
            logging.info(f"Executing CRUDStorageLocation.update: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.storage_locations.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_storage_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDStorageLocation.update: {error}")
            raise


# ====== TICKET CRUD ======

def _format_ticket_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB ticket document into standard schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDTicket:
    """Database persistence access layer for Ticket documents."""

    async def create(self, ticket_in: dict) -> dict:
        """Create a new ticket document."""
        try:
            logging.info("Executing CRUDTicket.create")
            db = MongoDatabase()
            data = dict(ticket_in)
            result = await db.tickets.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_ticket_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDTicket.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """Retrieve ticket document by unique MongoDB ObjectId hex string."""
        try:
            logging.info(f"Executing CRUDTicket.get_by_id: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.tickets.find_one({"_id": query_id})
            return _format_ticket_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDTicket.get_by_id: {error}")
            raise

    async def get_by_ticket_id(self, ticket_id: str) -> dict | None:
        """Retrieve ticket document by human-readable ticket_id string (e.g. RNO-20260813-001)."""
        try:
            logging.info(f"Executing CRUDTicket.get_by_ticket_id: {ticket_id}")
            db = MongoDatabase()
            doc = await db.tickets.find_one({"ticket_id": ticket_id.strip()})
            return _format_ticket_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDTicket.get_by_ticket_id: {error}")
            raise

    async def list_tickets(self, filter_query: dict | None = None, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """List tickets with filtering and pagination."""
        try:
            logging.info("Executing CRUDTicket.list_tickets")
            db = MongoDatabase()
            query = filter_query or {}
            total = await db.tickets.count_documents(query)
            cursor = db.tickets.find(query).sort("created_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [_format_ticket_doc(doc) for doc in docs], total
        except Exception as error:
            logging.error(f"Error in CRUDTicket.list_tickets: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """Update ticket fields by unique ID or ticket_id string."""
        try:
            logging.info(f"Executing CRUDTicket.update: {id}")
            db = MongoDatabase()
            filter_doc = {"_id": ObjectId(id)} if ObjectId.is_valid(id) else {"ticket_id": id}
            result = await db.tickets.find_one_and_update(
                filter_doc,
                {"$set": update_in},
                return_document=True,
            )
            return _format_ticket_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDTicket.update: {error}")
            raise


# ====== VOICE DRAFT CRUD ======

def _format_draft_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format raw MongoDB draft document into standard schema payload."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""
    return doc


class CRUDVoiceDraft:
    """Database persistence access layer for VoiceDraft documents."""

    async def create(self, draft_in: dict) -> dict:
        """Create a new voice draft document."""
        try:
            logging.info("Executing CRUDVoiceDraft.create")
            db = MongoDatabase()
            data = dict(draft_in)
            result = await db.voice_drafts.insert_one(data)
            data["_id"] = result.inserted_id
            return _format_draft_doc(data)
        except Exception as error:
            logging.error(f"Error in CRUDVoiceDraft.create: {error}")
            raise

    async def get_by_id(self, id: str) -> dict | None:
        """Retrieve voice draft by unique ID string."""
        try:
            logging.info(f"Executing CRUDVoiceDraft.get_by_id: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            doc = await db.voice_drafts.find_one({"_id": query_id})
            return _format_draft_doc(doc) if doc else None
        except Exception as error:
            logging.error(f"Error in CRUDVoiceDraft.get_by_id: {error}")
            raise

    async def update(self, id: str, update_in: dict) -> dict | None:
        """Update voice draft fields by unique ID."""
        try:
            logging.info(f"Executing CRUDVoiceDraft.update: {id}")
            db = MongoDatabase()
            query_id = ObjectId(id) if ObjectId.is_valid(id) else id
            result = await db.voice_drafts.find_one_and_update(
                {"_id": query_id},
                {"$set": update_in},
                return_document=True,
            )
            return _format_draft_doc(result) if result else None
        except Exception as error:
            logging.error(f"Error in CRUDVoiceDraft.update: {error}")
            raise
