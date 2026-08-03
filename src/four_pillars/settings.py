from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    artifact_dir: Path = Path("artifacts")
    database_url: str = "sqlite:///artifacts/jobs.sqlite3"
    report_retention_days: int = Field(default=30, ge=1, le=3650)
    api_key_sha256: str | None = None

    nvidia_api_key: str | None = None
    nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nim_model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
    nim_eval_model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
    nim_timeout_seconds: float = Field(default=120, gt=0, le=600)
    nim_max_retries: int = Field(default=3, ge=0, le=10)
    nim_max_schema_repairs: int = Field(default=1, ge=0, le=3)

    @property
    def sqlite_path(self) -> Path:
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix):
            raise ValueError("Only sqlite:/// database URLs are supported in v1")
        return Path(self.database_url.removeprefix(prefix))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
