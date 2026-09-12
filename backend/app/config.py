from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FOODFLOW"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://foodflow:foodflow@localhost:5432/foodflow"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "development-only-change-me-use-env-in-production-2026"
    jwt_access_minutes: int = 15
    jwt_refresh_days: int = 30
    cors_origins: str = "http://localhost:5173"
    openai_api_key: str | None = None
    map_api_key: str | None = None
    payment_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
