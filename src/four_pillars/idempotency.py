"""Validate HTTP idempotency keys and fingerprint canonical report requests."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

_STRUCTURED_STRING = re.compile(
    r'"(?:[\x20-\x21\x23-\x5B\x5D-\x7E]|\\["\\])*"\Z'
)
_MINIMUM_KEY_LENGTH = 8
_MAXIMUM_KEY_LENGTH = 128


def parse_idempotency_key(value: str) -> str:
    """Return the decoded RFC 8941 structured-string idempotency key.

    The product accepts printable ASCII structured strings whose decoded value is
    between 8 and 128 characters. Only the two RFC 8941 string escapes, ``\"``
    and ``\\``, are accepted. A fixed bounded syntax prevents ambiguous parsing,
    control characters, and unbounded database lookup keys.

    Args:
        value: Complete ``Idempotency-Key`` HTTP field value.

    Returns:
        The canonical decoded key without surrounding quotes.

    Raises:
        ValueError: When the field is not a supported structured string.
    """
    if _STRUCTURED_STRING.fullmatch(value) is None:
        raise ValueError("Invalid Idempotency-Key structured string")
    decoded = re.sub(r'\\(["\\])', r"\1", value[1:-1])
    if not _MINIMUM_KEY_LENGTH <= len(decoded) <= _MAXIMUM_KEY_LENGTH:
        raise ValueError("Idempotency-Key must decode to 8 through 128 characters")
    return decoded


def request_fingerprint(request: dict[str, Any]) -> str:
    """Return a canonical SHA-256 digest for one JSON-compatible request mapping."""
    canonical = json.dumps(
        request,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
