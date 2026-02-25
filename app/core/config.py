import logging
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ================= SERVER =================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_WORKERS: int = 1
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ================= DATABASE =================
    # Default SQLite for local development
    DATABASE_URL: str = "sqlite+aiosqlite:///./weather.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 300

    # ================= EXTERNAL APIs =================
    # Optional during development
    OPENWEATHER_API_KEY: str = ""
    GEOCODING_API_KEY: str = ""
    YOUTUBE_API_KEY: str = ""
    AQI_API_KEY: str = ""

    # ================= API SETTINGS =================
    API_TIMEOUT: int = 30
    API_RETRY_ATTEMPTS: int = 3
    API_RETRY_DELAY: int = 1

    # ================= CACHE =================
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = True

    # ================= HELPERS =================

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    def get_log_level(self) -> int:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(self.LOG_LEVEL.upper(), logging.INFO)


# Singleton settings instance
settings = Settings()