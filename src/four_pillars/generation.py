"""Define the structural client boundary for schema-validated LLM generation."""

from __future__ import annotations

from typing import Any, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

from .nim import NimTrace

T = TypeVar("T", bound=BaseModel)


@runtime_checkable
class StructuredGenerationClient(Protocol):
    """Generate one Pydantic-validated object from an untrusted evidence payload."""

    async def generate(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_model: type[T],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> tuple[T, NimTrace]:
        """Return one validated response and provider-neutral generation trace."""
        raise NotImplementedError  # pragma: no cover - protocol declaration
