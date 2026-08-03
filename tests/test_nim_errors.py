from __future__ import annotations

import httpx
import pytest
from pydantic import BaseModel

from four_pillars.nim import NimClient, NimError, NimSchemaError
from four_pillars.settings import Settings


class Answer(BaseModel):
    value: str


def config(**updates):
    data = {
        "nvidia_api_key": "key",
        "nim_base_url": "https://nim.test/v1",
        "nim_model": "model",
        "nim_max_retries": 0,
        "nim_max_schema_repairs": 0,
    }
    data.update(updates)
    return Settings(**data)


@pytest.mark.asyncio
async def test_markdown_fenced_json_is_accepted() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "```json\n{\"value\":\"ok\"}\n```"}}]},
        )

    async with NimClient(config(), transport=httpx.MockTransport(handler)) as client:
        answer, _ = await client.generate(
            system_prompt="JSON",
            user_payload={},
            response_model=Answer,
        )
    assert answer.value == "ok"


@pytest.mark.asyncio
async def test_non_retryable_http_error_fails_immediately() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="bad request")

    async with NimClient(config(), transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NimError, match="HTTP 400"):
            await client.generate(system_prompt="JSON", user_payload={}, response_model=Answer)


@pytest.mark.asyncio
async def test_missing_choices_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": "missing"})

    async with NimClient(config(), transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NimError, match="choices"):
            await client.generate(system_prompt="JSON", user_payload={}, response_model=Answer)


@pytest.mark.asyncio
async def test_non_json_content_exhausts_schema_repair() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "not json"}}]})

    async with NimClient(config(), transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NimSchemaError, match="schema validation"):
            await client.generate(system_prompt="JSON", user_payload={}, response_model=Answer)


@pytest.mark.asyncio
async def test_retryable_server_error_respects_retry_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    async with NimClient(config(), transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NimError, match="after retries"):
            await client.generate(system_prompt="JSON", user_payload={}, response_model=Answer)
