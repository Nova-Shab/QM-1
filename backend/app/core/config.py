"""
Application configuration settings.
GMP Documentation Management System - Pharma DMS
"""
from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "Pharma DMS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pharma_dms"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/pharma_dms"

    # Security
    SECRET_KEY: str = "pharma-dms-secret-key-change-in-production-2024"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # File storage (for prototype, using local paths)
    DOCUMENT_STORAGE_PATH: str = "./document_storage"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
