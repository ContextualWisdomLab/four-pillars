"""Separate a generation the provider cut short from a genuine success.

A chat-completions gateway reports ``finish_reason`` on each choice. When the
model hits the token ceiling the value is ``length`` and the content is a
prefix of the intended answer. Such a prefix can still parse and validate when
the schema's later fields are optional, so without this check a half-written
interpretation reaches the customer's report as if it were complete.
"""

from __future__ import annotations

import httpx
import pytest
from pydantic import BaseModel

from four_pillars.nim import NimClient, NimError, NimTruncationError
from four_pillars.settings import Settings


class Answer(BaseModel):
    """Accept a partial payload so truncation cannot be caught by validation alone."""

    value: str
    detail: str = ""


def config(**updates: object) -> Settings:
    """Build settings for a hosted client that never retries or repairs."""
    data: dict[str, object] = {
        "nvidia_nim_api_key": "key",
        "nim_base_url": "https://nim.test/v1",
        "nim_model": "model",
        "nim_max_retries": 0,
        "nim_max_schema_repairs": 0,
    }
    data.update(updates)
    return Settings(**data)


def _responder(payload: dict[str, object]) -> httpx.MockTransport:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    transport.calls = calls  # type: ignore[attr-defined]
    return transport


@pytest.mark.parametrize("reason", ["length", "max_tokens"])
@pytest.mark.asyncio
async def test_truncated_choice_is_not_a_success(reason: str) -> None:
    """A choice cut short at the token ceiling fails instead of returning a prefix."""
    transport = _responder(
        {
            "choices": [
                {"message": {"content": '{"value":"ok"}'}, "finish_reason": reason},
            ]
        }
    )

    async with NimClient(config(), transport=transport) as client:
        with pytest.raises(NimTruncationError, match=reason):
            await client.generate(system_prompt="JSON", user_payload={}, response_model=Answer)


@pytest.mark.asyncio
async def test_truncation_error_is_a_transport_error_not_a_schema_error() -> None:
    """Callers that already handle provider failures keep working unchanged."""
    assert issubclass(NimTruncationError, NimError)


@pytest.mark.asyncio
async def test_truncation_is_not_repaired_with_the_same_ceiling() -> None:
    """Re-asking under the same limit only truncates again, so it is never retried."""
    transport = _responder(
        {
            "choices": [
                {"message": {"content": '{"value":"ok"}'}, "finish_reason": "length"},
            ]
        }
    )

    async with NimClient(config(nim_max_schema_repairs=3), transport=transport) as client:
        with pytest.raises(NimTruncationError):
            await client.generate(system_prompt="JSON", user_payload={}, response_model=Answer)

    assert len(transport.calls) == 1  # type: ignore[attr-defined]


@pytest.mark.parametrize("reason", ["stop", None])
@pytest.mark.asyncio
async def test_a_complete_or_unreported_finish_reason_still_succeeds(
    reason: str | None,
) -> None:
    """An absent marker means unknown, not truncated, so nothing is invented."""
    choice: dict[str, object] = {"message": {"content": '{"value":"ok"}'}}
    if reason is not None:
        choice["finish_reason"] = reason

    async with NimClient(config(), transport=_responder({"choices": [choice]})) as client:
        answer, _ = await client.generate(system_prompt="JSON", user_payload={}, response_model=Answer)

    assert answer.value == "ok"
