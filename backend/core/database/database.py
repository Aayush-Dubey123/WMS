"""
database.py — MongoDB client and ODMantic connection manager.

Initializes Motor async client and ODMantic AIOEngine using singletons.
Provides raw database access for MongoDB transactions and aggregation pipelines.
"""


from motor import core, motor_asyncio
from odmantic import AIOEngine
from pymongo.driver_info import DriverInfo

from core import logger
from core.config.settings import settings

logging = logger(__name__)
DRIVER_INFO = DriverInfo(name="whitfield-wms", version="1.0.0")


class _MongoClientSingleton:
    """
    Singleton holding the async Motor client and ODMantic AIOEngine.

    Manages connection pooling across the lifecycle of the FastAPI application.
    Prevents duplicate database connection creation.
    """

    mongo_client: motor_asyncio.AsyncIOMotorClient | None = None
    engine: AIOEngine | None = None

    def __new__(cls):
        """
        Instantiate or return existing singleton instance.

        Creates Motor AsyncIOMotorClient and ODMantic AIOEngine on first call.

        Returns:
            _MongoClientSingleton: The shared singleton instance.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
            logging.info(
                f"Executing _MongoClientSingleton.__new__ | DB: {settings.DATABASE_NAME}"
            )
            cls.instance.mongo_client = motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URL, driver=DRIVER_INFO
            )
            cls.instance.engine = AIOEngine(
                client=cls.instance.mongo_client, database=settings.DATABASE_NAME
            )
            logging.info(
                f"MongoDB singleton initialized successfully | URI: {settings.MONGODB_URL}"
            )
        return cls.instance


def MongoDatabase() -> core.AgnosticDatabase:
    """
    Return raw Motor database instance.

    Used for raw MongoDB queries, transactions, and aggregations.

    Returns:
        core.AgnosticDatabase: Configured raw Motor database reference.
    """
    logging.info("Executing MongoDatabase function")
    return _MongoClientSingleton().mongo_client[settings.DATABASE_NAME]


def get_engine() -> AIOEngine:
    """
    Return ODMantic AIOEngine instance.

    Provides ODM engine reference for model-based persistence.

    Returns:
        AIOEngine: Shared ODMantic engine instance.
    """
    logging.info("Executing get_engine function")
    return _MongoClientSingleton().engine


def get_mongo_client() -> motor_asyncio.AsyncIOMotorClient:
    """
    Return raw Motor AsyncIOMotorClient instance.

    Used when initiating client sessions for multi-document MongoDB transactions.

    Returns:
        motor_asyncio.AsyncIOMotorClient: Shared Motor client instance.
    """
    logging.info("Executing get_mongo_client function")
    return _MongoClientSingleton().mongo_client


async def ping() -> bool:
    """
    Verify MongoDB connection health.

    Executes ping command against target MongoDB database.

    Returns:
        bool: True if database responds to ping command.

    Raises:
        Exception: If database ping fails or connection is unreachable.
    """
    try:
        logging.info("Executing ping function")
        await MongoDatabase().command("ping")
        logging.info("MongoDB ping successful")
        return True
    except Exception as error:
        logging.error(f"Error in ping function: {error}")
        raise


async def connect_to_mongo() -> None:
    """
    Initialize MongoDB connection at application startup.

    Instantiates client singleton and verifies database ping responsiveness.

    Raises:
        Exception: If database connection setup fails.
    """
    try:
        logging.info("Executing connect_to_mongo function")
        _MongoClientSingleton()
        await ping()
        logging.info("MongoDB connection established successfully")
    except Exception as error:
        logging.error(f"Error in connect_to_mongo function: {error}")
        raise


async def close_mongo_connection() -> None:
    """
    Close MongoDB client connections at application shutdown.

    Releases all active connection pool resources held by Motor.
    """
    try:
        logging.info("Executing close_mongo_connection function")
        singleton = _MongoClientSingleton()
        if singleton.mongo_client:
            singleton.mongo_client.close()
            logging.info("MongoDB connection closed successfully")
    except Exception as error:
        logging.error(f"Error in close_mongo_connection function: {error}")
