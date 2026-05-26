from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Prisma Factsheet API"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Default SQLite so the app runs locally without PostgreSQL/Docker.
    # For production, set DATABASE_URL to PostgreSQL in .env.
    database_url: str = "sqlite:///./data/prisma_factsheet.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    etl_cron_hour: int = 6
    etl_cron_minute: int = 0
    scheduler_enabled: bool = True

    log_level: str = "INFO"

    yfinance_lookback_years: int = 5
    risk_free_rate: float = 0.04


@lru_cache
def get_settings() -> Settings:
    return Settings()
