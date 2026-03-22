from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "College App API"
    app_env: str = "development"
    app_debug: bool = False
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    auto_create_schema: bool = False

    database_url: str = "sqlite:///./college_app.db"

    firebase_project_id: str | None = None
    firebase_credentials_json: str | None = None

    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    rate_limit_per_minute: int = 120
    upload_dir: str = "uploads"
    protect_metrics: bool = True
    metrics_token: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
