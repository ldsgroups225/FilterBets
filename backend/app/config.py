"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the root directory (parent of backend/)
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "FilterBets API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://filterbets:filterbets@localhost:5432/filterbets"
    database_url_sync: str = "postgresql://filterbets:filterbets@localhost:5432/filterbets"
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    celery_task_track_started: bool = True
    celery_task_time_limit: int = 3600  # 1 hour
    celery_task_soft_time_limit: int = 3300  # 55 minutes

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # JWT
    jwt_secret_key: str = "your-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Telegram Bot
    telegram_bot_token: str = ""
    telegram_bot_username: str = "filterbet_prematch_spy_bot"
    telegram_link_token_ttl: int = 1800  # 30 minutes in seconds

    # Scanner Configuration
    scanner_lookahead_hours: int = 24  # How far ahead to scan for fixtures
    scanner_max_notifications_per_scan: int = 1000  # Safety limit

    def get_allowed_origins_list(self) -> list[str]:
        """Get allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
