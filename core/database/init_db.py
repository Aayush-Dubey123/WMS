"""
init_db.py — Database initialization and index migration script.

Creates required MongoDB collections and sets up unique and compound indexes.
Ensures idempotency when executed on startup or migration drills.
"""

from pymongo import ASCENDING

from core import logger
from core.database.database import MongoDatabase

logging = logger(__name__)


async def init_db() -> None:
    """
    Initialize database collections and create required indexes.

    Creates unique and compound indexes for core system collections idempotently.

    Raises:
        Exception: If index creation fails during database setup.
    """
    try:
        logging.info("Executing init_db function")
        db = MongoDatabase()

        # Collection: users
        # Unique index on email
        await db.users.create_index(
            [("email", ASCENDING)],
            unique=True,
            name="idx_users_email_unique",
        )
        logging.info("Index created: users.email (unique)")

        # Collection: warehouses
        # Unique index on warehouse code
        await db.warehouses.create_index(
            [("code", ASCENDING)],
            unique=True,
            name="idx_warehouses_code_unique",
        )
        logging.info("Index created: warehouses.code (unique)")

        # Collection: inbox_shipments
        # Unique sparse index on tracking_number
        await db.inbox_shipments.create_index(
            [("tracking_number", ASCENDING)],
            unique=True,
            sparse=True,
            name="idx_inbox_tracking_unique",
        )
        logging.info("Index created: inbox_shipments.tracking_number (unique, sparse)")

        # Collection: tickets
        # Unique index on ticket_id
        await db.tickets.create_index(
            [("ticket_id", ASCENDING)],
            unique=True,
            name="idx_tickets_id_unique",
        )
        logging.info("Index created: tickets.ticket_id (unique)")

        # Collection: items
        # Compound unique index on ticket_id + unit_seq
        await db.items.create_index(
            [("ticket_id", ASCENDING), ("unit_seq", ASCENDING)],
            unique=True,
            name="idx_items_ticket_unit_seq_unique",
        )
        await db.items.create_index(
            [("barcode", ASCENDING)],
            name="idx_items_barcode",
        )
        logging.info(
            "Indexes created: items.ticket_id + unit_seq (unique), items.barcode"
        )

        # Collection: orders
        # Unique index on order_id
        await db.orders.create_index(
            [("order_id", ASCENDING)],
            unique=True,
            name="idx_orders_id_unique",
        )
        logging.info("Index created: orders.order_id (unique)")

        # Collection: storage_locations
        # Unique index on warehouse_id + location_code
        await db.storage_locations.create_index(
            [("warehouse_id", ASCENDING), ("location_code", ASCENDING)],
            unique=True,
            name="idx_storage_location_unique",
        )
        logging.info(
            "Index created: storage_locations.warehouse_id + location_code (unique)"
        )

        # Collection: counters
        # Compound unique index on wh_code + date_str
        await db.counters.create_index(
            [("wh_code", ASCENDING), ("date_str", ASCENDING)],
            unique=True,
            name="idx_counters_wh_date_unique",
        )
        logging.info("Index created: counters.wh_code + date_str (unique)")

        # Collection: api_keys
        # Unique index on key_hash
        await db.api_keys.create_index(
            [("key_hash", ASCENDING)],
            unique=True,
            name="idx_api_keys_hash_unique",
        )
        logging.info("Index created: api_keys.key_hash (unique)")

        # Collection: idempotency_keys
        # Unique index on key
        await db.idempotency_keys.create_index(
            [("key", ASCENDING)],
            unique=True,
            name="idx_idempotency_key_unique",
        )
        logging.info("Index created: idempotency_keys.key (unique)")

        logging.info("Database initialization and index creation completed successfully")
    except Exception as error:
        logging.error(f"Error in init_db function: {error}")
        raise
