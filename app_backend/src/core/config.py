from functools import lru_cache
from typing import List
import os

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from .secrets import get_secret_cached


class Settings(BaseSettings):
    app_name: str = "College App API"
    app_env: str = "development"
    app_debug: bool = False
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    auto_create_schema: bool = False

    database_url: str

    gcp_project_id: str = ""
    secrets_provider: str = "env"
    storage_provider: str = "local"
    gcs_bucket_name: str = ""

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

    @field_validator("secrets_provider", mode="before")
    @classmethod
    def normalize_secrets_provider(cls, value):
        if value is None or value == "":
            return os.environ.get("SECRETS_PROVIDER", "env").lower()
        return str(value).lower()

    @model_validator(mode="before")
    @classmethod
    def load_required_secrets(cls, values):
        if values is None:
            values = {}
        if not isinstance(values, dict):
            return values

        provider = str(
            values.get("secrets_provider")
            or os.environ.get("SECRETS_PROVIDER", "env")
        ).lower()

        if not values.get("database_url"):
            values["database_url"] = get_secret_cached("DATABASE_URL")
        if provider == "gcp" and not values.get("firebase_credentials_json"):
            values["firebase_credentials_json"] = get_secret_cached("FIREBASE_CREDENTIALS_JSON")

        return values


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
