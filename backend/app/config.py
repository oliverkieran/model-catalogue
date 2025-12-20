"""
Application Configuration
Manages environment variables and settings using Pydantic
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    app_name: str = "Model Catalogue API"
    debug: bool = False

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/model_catalogue"
    database_url_async: str = (
        "postgresql+asyncpg://user:password@localhost:5432/model_catalogue"
    )

    # LLM Service
    anthropic_api_key: str = ""

    # RSS Feed
    rss_feed_url: str = ""

    # Scheduler
    enable_scheduler: bool = True
    schedule_cron: str = "0 9 * * 1-5"  # 9 AM, Monday-Friday

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


# Global settings instance
settings = Settings()
