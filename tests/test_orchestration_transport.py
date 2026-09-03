"""Exercise the provider-neutral OpenAI-compatible orchestration transport."""

from __future__ import annotations

import json

import httpx
import pytest
from pydantic import BaseModel

import four_pillars.infrastructure.orchestration.openai_compatible as transport_module
from four_pillars.infrastructure.orchestration.openai_compatible import (
    OpenAICompatibleJsonClient,
    OrchestrationSchemaError,
    OrchestrationTransportError,
)


class Answer(BaseModel):
    """Minimal structured response used by transport tests."""

    value: str


def client(
    *,
    transport: httpx.AsyncBaseTransport,
    max_retries: int = 0,
    max_schema_repairs: int = 0,
    native_json_mode: bool = False,
) -> OpenAICompatibleJsonClient:
    """Build an isolated transport without any provider-specific configuration."""
    return OpenAICompatibleJsonClient(
        api_key="test-gateway-key",
        base_url="https://gateway.test/v1",
        default_model="virtual-test-route",
        timeout_seconds=30,
        max_retries=max_retries,
        max_schema_repairs=max_schema_repairs,
        service_label="Test Gateway",
        native_json_mode=native_json_mode,
        transport=transport,
    )


@pytest.mark.asyncio
async def test_transport_sends_bearer_auth_and_optional_native_json_mode() -> None:
    """Keep generic envelope support testable without making it a product route."""
    observed: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["authorization"] = request.headers["Authorization"]
        observed["path"] = request.url.path
        observed["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"value":"ok"}'}}]},
        )

    async with client(
        transport=httpx.MockTransport(handler),
        native_json_mode=True,
    ) as gateway:
        answer, trace = await gateway.generate(
            system_prompt="Return JSON.",
            user_payload={"calculation": {"fingerprint": "abc"}},
            response_model=Answer,
        )

    body = observed["body"]
    assert isinstance(body, dict)
    assert answer.value == "ok"
    assert trace.model == "virtual-test-route"
    assert trace.attempts == 1
    assert observed["authorization"] == "Bearer test-gateway-key"
    assert observed["path"] == "/v1/chat/completions"
    assert body["model"] == "virtual-test-route"
    assert body["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_invalid_first_response_gets_one_schema_repair() -> None:
    """Retry schema-invalid content once when the configured budget permits it."""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        content = "{}" if calls == 1 else '{"value":"fixed"}'
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": content}}]},
        )

    async with client(
        transport=httpx.MockTransport(handler),
        max_schema_repairs=1,
    ) as gateway:
        answer, trace = await gateway.generate(
            system_prompt="Return JSON.",
            user_payload={},
            response_model=Answer,
        )

    assert answer.value == "fixed"
    assert calls == 2
    assert trace.repairs == 1


@pytest.mark.asyncio
async def test_rate_limit_is_retried() -> None:
    """Retry a transient rate limit without changing the virtual route."""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                429,
                headers={"Retry-After": "0"},
                json={"error": "rate"},
            )
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"value":"ok"}'}}]},
        )

    async with client(
        transport=httpx.MockTransport(handler),
        max_retries=1,
    ) as gateway:
        answer, trace = await gateway.generate(
            system_prompt="Return JSON.",
            user_payload={},
            response_model=Answer,
        )

    assert answer.value == "ok"
    assert calls == 2
    assert trace.attempts == 2


@pytest.mark.asyncio
async def test_markdown_fenced_json_is_accepted() -> None:
    """Accept a common fenced JSON response after deterministic unwrapping."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": '```json\n{"value":"ok"}\n```'}}
                ]
            },
        )

    async with client(transport=httpx.MockTransport(handler)) as gateway:
        answer, _ = await gateway.generate(
            system_prompt="JSON",
            user_payload={},
            response_model=Answer,
        )

    assert answer.value == "ok"


@pytest.mark.asyncio
async def test_non_retryable_http_error_fails_immediately() -> None:
    """Do not hide caller errors behind retry loops."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="bad request")

    async with client(transport=httpx.MockTransport(handler)) as gateway:
        with pytest.raises(OrchestrationTransportError, match="HTTP 400"):
            await gateway.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


@pytest.mark.asyncio
async def test_missing_choices_is_rejected() -> None:
    """Reject an invalid OpenAI-compatible response envelope."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": "missing"})

    async with client(transport=httpx.MockTransport(handler)) as gateway:
        with pytest.raises(OrchestrationTransportError, match="choices"):
            await gateway.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


@pytest.mark.asyncio
async def test_non_json_content_exhausts_schema_repair() -> None:
    """Fail closed when generated content is not a JSON object."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "not json"}}]},
        )

    async with client(transport=httpx.MockTransport(handler)) as gateway:
        with pytest.raises(OrchestrationSchemaError, match="schema validation"):
            await gateway.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


@pytest.mark.asyncio
async def test_retryable_server_error_respects_retry_limit() -> None:
    """Stop retrying after the configured server-error budget is exhausted."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    async with client(transport=httpx.MockTransport(handler)) as gateway:
        with pytest.raises(OrchestrationTransportError, match="after retries"):
            await gateway.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


@pytest.mark.asyncio
async def test_network_failures_retry_and_then_succeed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Retry a transient network failure within the bounded transport budget."""
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

    monkeypatch.setattr(transport_module.asyncio, "sleep", no_sleep)
    async with client(
        transport=httpx.MockTransport(handler),
        max_retries=1,
    ) as gateway:
        answer, trace = await gateway.generate(
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
    """Raise a transport error after the network retry budget is exhausted."""
    calls = 0

    async def no_sleep(_: float) -> None:
        return None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("offline", request=request)

    monkeypatch.setattr(transport_module.asyncio, "sleep", no_sleep)
    async with client(
        transport=httpx.MockTransport(handler),
        max_retries=1,
    ) as gateway:
        with pytest.raises(OrchestrationTransportError, match="network retries"):
            await gateway.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )

    assert calls == 2


@pytest.mark.asyncio
async def test_non_json_http_payload_is_rejected() -> None:
    """Reject a successful HTTP response whose envelope is not JSON."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    async with client(transport=httpx.MockTransport(handler)) as gateway:
        with pytest.raises(OrchestrationTransportError, match="non-JSON HTTP response"):
            await gateway.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


@pytest.mark.parametrize("content", ["", None])
@pytest.mark.asyncio
async def test_empty_or_non_string_content_is_rejected(content: object) -> None:
    """Reject absent model content before schema parsing."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": content}}]},
        )

    async with client(transport=httpx.MockTransport(handler)) as gateway:
        with pytest.raises(OrchestrationTransportError, match="empty content"):
            await gateway.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


def test_json_object_parser_covers_incomplete_fences_and_non_objects() -> None:
    """Fail deterministically on malformed fences and non-object JSON values."""
    assert OpenAICompatibleJsonClient._json_object(
        '```json\n{"value":"ok"}'
    ) == {"value": "ok"}
    with pytest.raises(OrchestrationSchemaError, match="not a JSON object"):
        OpenAICompatibleJsonClient._json_object("```")
    with pytest.raises(OrchestrationSchemaError, match="one JSON object"):
        OpenAICompatibleJsonClient._json_object("[]")


def unreachable_handler(request: httpx.Request) -> httpx.Response:
    """Fail a test when an impossible budget unexpectedly performs I/O."""
    raise AssertionError(f"unexpected HTTP request: {request.url}")


@pytest.mark.asyncio
async def test_post_detects_an_impossible_empty_attempt_budget() -> None:
    """Cover the defensive terminal branch for an impossible negative retry budget."""
    async with client(
        transport=httpx.MockTransport(unreachable_handler),
        max_retries=-1,
    ) as gateway:
        with pytest.raises(OrchestrationTransportError, match="exhausted its retry budget"):
            await gateway._post({})


@pytest.mark.asyncio
async def test_generate_detects_an_impossible_empty_repair_budget() -> None:
    """Cover the defensive terminal branch for an impossible negative repair budget."""
    async with client(
        transport=httpx.MockTransport(unreachable_handler),
        max_schema_repairs=-1,
    ) as gateway:
        with pytest.raises(OrchestrationSchemaError, match="unreachable schema repair state"):
            await gateway.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )
