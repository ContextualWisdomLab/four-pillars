"""Verify credential-bearing model endpoints use HTTPS or local loopback HTTP."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from four_pillars.settings import Settings


@pytest.mark.parametrize(
    "field_name",
    ("nim_base_url", "contextual_orchestrator_base_url"),
)
def test_remote_http_model_endpoint_is_rejected(field_name: str) -> None:
    """Reject a remote cleartext URL before a Bearer token can be transmitted."""
    with pytest.raises(ValidationError, match="HTTPS or loopback HTTP"):
        Settings(**{field_name: "http://models.example.com/v1"})


@pytest.mark.parametrize(
    "url",
    (
        "http://localhost:8100/v1",
        "http://127.0.0.1:8100/v1",
        "http://[::1]:8100/v1",
        "https://models.example.com/v1",
    ),
)
def test_secure_or_loopback_model_endpoint_is_accepted(url: str) -> None:
    """Allow TLS endpoints and explicit loopback development endpoints."""
    configured = Settings(
        nim_base_url=url,
        contextual_orchestrator_base_url=url,
    )

    assert configured.nim_base_url == url
    assert configured.contextual_orchestrator_base_url == url


@pytest.mark.parametrize(
    "url",
    (
        "models.example.com/v1",
        "ftp://models.example.com/v1",
        "https:///missing-host",
        "http://0.0.0.0:8100/v1",
    ),
)
def test_invalid_model_endpoint_is_rejected(url: str) -> None:
    """Reject malformed, unsupported, hostless, and non-loopback cleartext URLs."""
    with pytest.raises(ValidationError, match="HTTPS or loopback HTTP"):
        Settings(nim_base_url=url)
