from __future__ import annotations

import os

import pytest
from pydantic import BaseModel

from four_pillars.nim import NimClient
from four_pillars.settings import Settings


class LiveAnswer(BaseModel):
    status: str
    korean_sentence: str


@pytest.mark.nim_live
@pytest.mark.asyncio
async def test_hosted_nim_returns_schema_valid_korean_json() -> None:
    if not os.getenv("NVIDIA_NIM_API_KEY"):
        pytest.skip("NVIDIA_NIM_API_KEY is not configured")
    settings = Settings()
    async with NimClient(settings) as client:
        result, trace = await client.generate(
            system_prompt=(
                "Return exactly one JSON object with status='ok' and one neutral Korean sentence "
                "explaining that a calendar calculation and an interpretation are different."
            ),
            user_payload={"test": "hosted NVIDIA NIM contract"},
            response_model=LiveAnswer,
            temperature=0,
            max_tokens=256,
        )
    assert result.status == "ok"
    assert len(result.korean_sentence) >= 10
    assert trace.model == settings.nim_model
