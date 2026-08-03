from __future__ import annotations

import json

import httpx
import pytest
from pydantic import BaseModel

from four_pillars.nim import NimClient, NimError
from four_pillars.settings import Settings


class Answer(BaseModel):
    title: str
    actions: list[str]


def settings(**updates):
    values = {
        "nvidia_nim_api_key": "test-key",
        "nim_base_url": "https://nim.test/v1",
        "nim_model": "free-test-model",
        "nim_max_retries": 2,
        "nim_max_schema_repairs": 1,
    }
    values.update(updates)
    return Settings(**values)


@pytest.mark.asyncio
async def test_nim_sends_bearer_auth_and_returns_validated_json() -> None:
    observed = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["authorization"] = request.headers["Authorization"]
        observed["path"] = request.url.path
        observed["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"title":"결과","actions":["기록합니다."]}'}}]},
        )

    async with NimClient(settings(), transport=httpx.MockTransport(handler)) as client:
        answer, trace = await client.generate(
            system_prompt="Return JSON.",
            user_payload={"calculation": {"fingerprint": "abc"}},
            response_model=Answer,
        )
    assert answer.title == "결과"
    assert trace.attempts == 1
    assert observed["authorization"] == "Bearer test-key"
    assert observed["path"] == "/v1/chat/completions"
    assert observed["body"]["model"] == "free-test-model"
    assert observed["body"]["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_invalid_first_response_gets_one_schema_repair() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        content = '{"title":"누락"}' if calls == 1 else '{"title":"수정","actions":["확인합니다."]}'
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    async with NimClient(settings(), transport=httpx.MockTransport(handler)) as client:
        answer, trace = await client.generate(
            system_prompt="Return JSON.",
            user_payload={},
            response_model=Answer,
        )
    assert answer.title == "수정"
    assert calls == 2
    assert trace.repairs == 1


@pytest.mark.asyncio
async def test_rate_limit_is_retried() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"error": "rate"})
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"title":"성공","actions":["기록합니다."]}'}}]},
        )

    async with NimClient(settings(), transport=httpx.MockTransport(handler)) as client:
        answer, trace = await client.generate(
            system_prompt="Return JSON.",
            user_payload={},
            response_model=Answer,
        )
    assert answer.title == "성공"
    assert calls == 2
    assert trace.attempts == 2


def test_missing_nvidia_nim_key_fails_without_provider_fallback() -> None:
    with pytest.raises(NimError, match="NVIDIA_NIM_API_KEY"):
        NimClient(settings(nvidia_nim_api_key=None))
