import os
from dataclasses import field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )
    PRODUCTION: bool = os.getenv("ENV") == "production"

    STATIC_PATH: str = "/static"
    BACKEND_CORS_ORIGINS: list[str] = field(default_factory=lambda: ["*"])  # TODO

    # PostgreSQL
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgres")
    POSTGRES_URI: str = (
                f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_URL}:5432/{POSTGRES_DB}"
    )

    # MongoDB
    MONGO_DB: str = os.getenv("MONGO_DB", "mongo")
    MONGO_URL: str = os.getenv("MONGO_URL", "mongo")
    MONGO_URI: str = f"mongodb://{MONGO_URL}:27017/"


settings = Settings()
