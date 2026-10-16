"""
Application configuration loaded from environment variables.

Uses pydantic-settings for type-safe, validated config.
All secrets come from .env — nothing is hardcoded.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, populated from .env or environment."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/bankops"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS — stored as string, parsed in main.py
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Application
    app_name: str = "BankOps"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
