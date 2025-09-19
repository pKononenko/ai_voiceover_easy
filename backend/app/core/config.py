from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_STORAGE_DIR = BASE_DIR / "storage" / "audio"
DEFAULT_DATABASE_URL = f"sqlite:///{(BASE_DIR / 'voiceover.db').as_posix()}"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="AI Voiceover Easy")
    secret_key: str = Field(default="change-me")
    access_token_expire_minutes: int = Field(default=60 * 24)
    database_url: str = Field(default=DEFAULT_DATABASE_URL)
    storage_dir: Path = Field(default=DEFAULT_STORAGE_DIR)
    allow_registration: bool = Field(default=True)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return settings
