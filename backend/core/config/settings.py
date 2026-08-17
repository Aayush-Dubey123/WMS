"""
settings.py — Application configuration management.

Provides typed environment variable loading using pydantic-settings.
Centralizes database connection parameters, JWT secrets, and runtime settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from core import logger

logging = logger(__name__)


class Settings(BaseSettings):
    """
    Application environment configuration settings.

    Loads runtime configurations from environment variables or .env file.
    Provides typed access to database URLs, JWT keys, and domain parameters.
    """

    APP_NAME: str = "Whitfield Fulfillment WMS"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True

    MONGODB_URL: str = "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true"
    DATABASE_NAME: str = "wms"
    MONGO_URI: str = "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true"
    MONGO_DB: str = "wms"

    SECRET_KEY: str = "your_super_secret_jwt_key_change_this_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DOMAIN: str = "localhost:8000"
    BASE_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """
    Retrieve application settings instance.

    Instantiates and returns the configured Settings object.

    Returns:
        Settings: Application configuration settings instance.
    """
    logging.info("Executing get_settings function")
    return Settings()


settings = get_settings()
