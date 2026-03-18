from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./content_platform.db"

    # Tongyi Qianwen
    dashscope_api_key: str = ""

    # DingDing
    dingding_webhook_url: str = ""
    dingding_secret: str = ""

    # Image APIs
    unsplash_access_key: str = ""
    pexels_api_key: str = ""

    # App
    environment: str = "development"
    log_level: str = "INFO"
    output_dir: str = "./output"
    assets_dir: str = "./assets"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Scheduler
    crawl_cron_hour: int = 6
    topic_push_cron_hour: int = 7

    # Paths
    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def config_dir(self) -> Path:
        return self.project_root.parent / "config"

    @property
    def output_path(self) -> Path:
        p = Path(self.output_dir)
        if not p.is_absolute():
            p = self.project_root / p
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def assets_path(self) -> Path:
        p = Path(self.assets_dir)
        if not p.is_absolute():
            p = self.project_root / p
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache
def get_settings() -> Settings:
    return Settings()
