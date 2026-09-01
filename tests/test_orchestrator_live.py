"""Opt-in live smoke test for the Contextual Orchestrator free pool."""

from __future__ import annotations

import os

import pytest
from pydantic import BaseModel

from four_pillars.contextual_orchestrator import ContextualOrchestratorClient
from four_pillars.settings import Settings


class LiveAnswer(BaseModel):
    """Minimal live response contract."""

    status: str
    korean_sentence: str


@pytest.mark.orchestrator_live
@pytest.mark.asyncio
async def test_orchestrator_free_returns_schema_valid_korean_json() -> None:
    """Exercise the same virtual model used by the product runtime."""
    if not os.getenv("CONTEXTUAL_ORCHESTRATOR_TOKEN"):
        pytest.skip("CONTEXTUAL_ORCHESTRATOR_TOKEN is not configured")
    if not os.getenv("CONTEXTUAL_ORCHESTRATOR_BASE_URL"):
        pytest.skip("CONTEXTUAL_ORCHESTRATOR_BASE_URL is not configured")

    settings = Settings()
    async with ContextualOrchestratorClient(settings) as client:
        result, trace = await client.generate(
            system_prompt=(
                "Return exactly one JSON object with status='ok' and one neutral Korean sentence "
                "explaining that a calendar calculation and an interpretation are different."
            ),
            user_payload={"test": "Contextual Orchestrator free-pool contract"},
            response_model=LiveAnswer,
            temperature=0,
            max_tokens=256,
        )

    assert result.status == "ok"
    assert len(result.korean_sentence) >= 10
    assert trace.model == "orchestrator/free"
