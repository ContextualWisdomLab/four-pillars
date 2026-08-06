"""Call Contextual Orchestrator through its OpenAI-compatible structured API."""

from __future__ import annotations

from typing import Any

import httpx

from .nim import (
    NimError,
    NimSchemaError,
    _OpenAICompatibleJsonClient,
)
from .settings import Settings

ContextualOrchestratorError = NimError
ContextualOrchestratorSchemaError = NimSchemaError


class ContextualOrchestratorClient(_OpenAICompatibleJsonClient):
    """Generate strict JSON through the organization model-orchestration gateway."""

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Create an authenticated orchestrator client and prompt-safe attribution."""
        if not settings.contextual_orchestrator_token:
            raise ContextualOrchestratorError(
                "CONTEXTUAL_ORCHESTRATOR_TOKEN is required when "
                "INTERPRETATION_BACKEND=contextual_orchestrator"
            )
        self.settings = settings
        attribution: dict[str, str] = {"service": "four-pillars"}
        optional_dimensions = {
            "account": settings.contextual_orchestrator_account,
            "team": settings.contextual_orchestrator_team,
            "group": settings.contextual_orchestrator_group,
            "company": settings.contextual_orchestrator_company,
        }
        for dimension, value in optional_dimensions.items():
            if value:
                attribution[dimension] = value
        request_metadata: dict[str, Any] = {
            "mode": settings.contextual_orchestrator_mode,
            "include_orchestration_trace": False,
            "attribution": attribution,
            "routing": {
                "channel": "sync",
                "latency_tolerant": False,
                "priority": "normal",
            },
        }
        super().__init__(
            api_key=settings.contextual_orchestrator_token,
            base_url=settings.contextual_orchestrator_base_url,
            default_model=settings.contextual_orchestrator_model,
            timeout_seconds=settings.contextual_orchestrator_timeout_seconds,
            max_retries=settings.contextual_orchestrator_max_retries,
            max_schema_repairs=(
                settings.contextual_orchestrator_max_schema_repairs
            ),
            provider_label="Contextual Orchestrator",
            request_metadata=request_metadata,
            native_json_mode=False,
            transport=transport,
        )
