from __future__ import annotations

import httpx
import pytest
from pydantic import BaseModel

import four_pillars.nim as nim_module
from four_pillars.settings import Settings


class Answer(BaseModel):
    value: str


def nim_settings(**updates: object) -> Settings:
    values: dict[str, object] = {
        "nvidia_nim_api_key": "test-key",
        "nim_base_url": "https://nim.test/v1",
        "nim_model": "test-model",
        "nim_max_retries": 0,
        "nim_max_schema_repairs": 0,
    }
    values.update(updates)
    return Settings(**values)


@pytest.mark.asyncio
async def test_network_failures_retry_and_then_succeed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def no_sleep(_: float) -> None:
        return None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ReadTimeout("timed out", request=request)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"value":"ok"}'}}]},
        )

    monkeypatch.setattr(nim_module.asyncio, "sleep", no_sleep)
    async with nim_module.NimClient(
        nim_settings(nim_max_retries=1),
        transport=httpx.MockTransport(handler),
    ) as client:
        answer, trace = await client.generate(
            system_prompt="JSON",
            user_payload={},
            response_model=Answer,
        )

    assert answer.value == "ok"
    assert trace.attempts == 2


@pytest.mark.asyncio
async def test_network_failures_stop_at_the_retry_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def no_sleep(_: float) -> None:
        return None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("offline", request=request)

    monkeypatch.setattr(nim_module.asyncio, "sleep", no_sleep)
    async with nim_module.NimClient(
        nim_settings(nim_max_retries=1),
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(nim_module.NimError, match="network retries"):
            await client.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )

    assert calls == 2


@pytest.mark.asyncio
async def test_non_json_http_payload_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    async with nim_module.NimClient(
        nim_settings(),
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(nim_module.NimError, match="non-JSON HTTP response"):
            await client.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


@pytest.mark.parametrize("content", ["", None])
@pytest.mark.asyncio
async def test_empty_or_non_string_nim_content_is_rejected(content: object) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": content}}]},
        )

    async with nim_module.NimClient(
        nim_settings(),
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(nim_module.NimError, match="empty content"):
            await client.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


def test_json_object_parser_covers_incomplete_fences_and_non_objects() -> None:
    assert nim_module.NimClient._json_object('```json\n{"value":"ok"}') == {"value": "ok"}
    with pytest.raises(nim_module.NimSchemaError, match="not a JSON object"):
        nim_module.NimClient._json_object("```")
    with pytest.raises(nim_module.NimSchemaError, match="one JSON object"):
        nim_module.NimClient._json_object("[]")


def unreachable_handler(request: httpx.Request) -> httpx.Response:
    raise AssertionError(f"unexpected HTTP request: {request.url}")


@pytest.mark.asyncio
async def test_post_detects_an_impossible_empty_attempt_budget() -> None:
    settings = Settings.model_construct(
        nvidia_nim_api_key="test-key",
        nim_base_url="https://nim.test/v1",
        nim_model="test-model",
        nim_timeout_seconds=120.0,
        nim_max_retries=-1,
        nim_max_schema_repairs=0,
    )
    async with nim_module.NimClient(
        settings,
        transport=httpx.MockTransport(unreachable_handler),
    ) as client:
        with pytest.raises(nim_module.NimError, match="exhausted its retry budget"):
            await client._post({})


@pytest.mark.asyncio
async def test_generate_detects_an_impossible_empty_repair_budget() -> None:
    settings = Settings.model_construct(
        nvidia_nim_api_key="test-key",
        nim_base_url="https://nim.test/v1",
        nim_model="test-model",
        nim_timeout_seconds=120.0,
        nim_max_retries=0,
        nim_max_schema_repairs=-1,
    )
    async with nim_module.NimClient(
        settings,
        transport=httpx.MockTransport(unreachable_handler),
    ) as client:
        with pytest.raises(nim_module.NimSchemaError, match="unreachable schema repair state"):
            await client.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )
