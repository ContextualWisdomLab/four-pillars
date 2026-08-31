"""Load validated runtime, storage, authentication, and interpretation configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

InterpretationBackend = Literal["nvidia_nim", "contextual_orchestrator"]
ContextualOrchestrationMode = Literal["auto", "route", "conduct"]
_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


class Settings(BaseSettings):
    """Environment-backed application settings with bounded operational values."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    artifact_dir: Path = Path("artifacts")
    database_url: str = "sqlite:///artifacts/jobs.sqlite3"
    report_retention_days: int = Field(default=30, ge=1, le=3650)
    api_key_sha256: str | None = None

    interpretation_backend: InterpretationBackend = "nvidia_nim"

    nvidia_nim_api_key: str | None = None
    nim_base_url: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        min_length=1,
        max_length=2048,
    )
    nim_model: str = Field(
        default="nvidia/llama-3.3-nemotron-super-49b-v1.5",
        min_length=1,
        max_length=256,
    )
    nim_eval_model: str = Field(
        default="nvidia/llama-3.3-nemotron-super-49b-v1.5",
        min_length=1,
        max_length=256,
    )
    nim_timeout_seconds: float = Field(default=120, gt=0, le=600)
    nim_max_retries: int = Field(default=3, ge=0, le=10)
    nim_max_schema_repairs: int = Field(default=1, ge=0, le=3)

    contextual_orchestrator_base_url: str = Field(
        default="http://127.0.0.1:8100/v1",
        min_length=1,
        max_length=2048,
    )
    contextual_orchestrator_token: str | None = None
    contextual_orchestrator_model: str = Field(
        default="contextual-orchestrator",
        min_length=1,
        max_length=256,
    )
    contextual_orchestrator_mode: ContextualOrchestrationMode = "auto"
    contextual_orchestrator_timeout_seconds: float = Field(
        default=2 * 60 * 60,
        gt=0,
        le=4 * 60 * 60,
        description="Timeout for each Contextual Orchestrator HTTP request",
    )
    contextual_orchestrator_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
    )
    contextual_orchestrator_max_schema_repairs: int = Field(
        default=1,
        ge=0,
        le=3,
    )
    contextual_orchestrator_account: str = Field(default="", max_length=128)
    contextual_orchestrator_team: str = Field(default="", max_length=128)
    contextual_orchestrator_group: str = Field(default="", max_length=128)
    contextual_orchestrator_company: str = Field(
        default="ContextualWisdomLab",
        max_length=128,
    )

    @field_validator("nim_base_url", "contextual_orchestrator_base_url")
    @classmethod
    def validate_credential_endpoint(cls, value: str) -> str:
        """Require HTTPS remotely and allow cleartext only on an explicit loopback host."""
        parsed = urlsplit(value)
        hostname = parsed.hostname
        valid_https = parsed.scheme == "https" and bool(hostname)
        valid_loopback_http = parsed.scheme == "http" and hostname in _LOOPBACK_HOSTS
        if not (valid_https or valid_loopback_http):
            raise ValueError(
                "Credential-bearing model endpoints require HTTPS or loopback HTTP"
            )
        return value

    @property
    def sqlite_path(self) -> Path:
        """Return the local path encoded by the supported ``sqlite:///`` database URL."""
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix):
            raise ValueError("Only sqlite:/// database URLs are supported in v1")
        return Path(self.database_url.removeprefix(prefix))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings object loaded from environment and ``.env``."""
    return Settings()
