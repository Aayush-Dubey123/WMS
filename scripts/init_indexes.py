"""
init_indexes.py — Script to initialize MongoDB indexes and list all collections.

Executes init_db to create indexes and then lists all database collections.
"""

import asyncio

from core.database.database import MongoDatabase
from core.database.init_db import init_db


async def main() -> None:
    await init_db()
    db = MongoDatabase()
    collections = await db.list_collection_names()
    print("Database index initialization completed successfully.")
    print("Collections list:")
    for col in sorted(collections):
        print(f" - {col}")


if __name__ == "__main__":
    asyncio.run(main())
