"""Application configuration loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # GLM / z.ai
    zai_api_key: str = ""
    zai_model: str = "glm-4.7-flash"
    zai_base_url: str = "https://api.z.ai/api/paas/v4"

    # Database
    database_url: str = "sqlite+aiosqlite:///./price_radar.db"

    # Scraping
    scrape_interval_min: int = 30
    scrape_limit_per_store: int = 60
    scrape_max_pages: int = 5  # max category pages to crawl (baku/w-t pagination)
    scrape_enabled: bool = True

    # i18n
    supported_langs: tuple[str, ...] = ("az", "ru", "en")
    default_lang: str = "az"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
