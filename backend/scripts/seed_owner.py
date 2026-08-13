"""
seed_owner.py — Initial Owner user bootstrap script.

Seeds default Owner account if no Owner exists in the users collection.
Run with: python -m scripts.seed_owner
"""

import asyncio
import os
import sys

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime

from pytz import timezone

from commons.auth import hash_password
from core import logger
from core.database.database import (
    MongoDatabase,
    close_mongo_connection,
    connect_to_mongo,
)
from core.models.user_model import UserRole, UserStatus

logging = logger(__name__)


async def seed_owner() -> None:
    """
    Seed initial Owner account in users collection if absent.

    Creates default Owner account (owner@whitfield.com / OwnerPass123!).
    """
    try:
        logging.info("Executing seed_owner function")
        await connect_to_mongo()
        db = MongoDatabase()

        existing_owner = await db.users.find_one({"role": UserRole.OWNER.value})
        if existing_owner:
            logging.info(f"Owner account already exists: {existing_owner.get('email')}")
            return

        owner_email = os.getenv("OWNER_EMAIL", "owner@whitfield.com")
        owner_password = os.getenv("OWNER_PASSWORD", "OwnerPass123!")

        owner_doc = {
            "email": owner_email,
            "full_name": "System Owner",
            "hashed_password": hash_password(owner_password),
            "role": UserRole.OWNER.value,
            "warehouse_id": None,
            "experience_tier": None,
            "function_roles": [],
            "status": UserStatus.ACTIVE.value,
            "created_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.now(timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S.%f"),
        }

        result = await db.users.insert_one(owner_doc)
        logging.info(f"Initial Owner account created successfully! ID: {result.inserted_id} | Email: {owner_email}")
    except Exception as error:
        logging.error(f"Error in seed_owner function: {error}")
        raise
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(seed_owner())
