"""Encode and decode privacy-safe keyset cursors for report-job history."""

from __future__ import annotations

import base64
import binascii
import json
import re
import uuid
from datetime import UTC, datetime, timedelta

_CURSOR_ERROR = "Invalid report-history cursor"
_CURSOR_VERSION = "v1"
_CURSOR_MAX_LENGTH = 256
_CURSOR_TOKEN = re.compile(r"^[A-Za-z0-9_-]+$")
_CURSOR_KEYS = frozenset({"created_at", "job_id"})


class HistoryCursorError(ValueError):
    """Signal malformed or unsupported report-history continuation input."""


def _validated_values(created_at: datetime, job_id: str) -> tuple[datetime, str]:
    try:
        if created_at.tzinfo is None or created_at.utcoffset() != timedelta(0):
            raise ValueError
        normalized = created_at.astimezone(UTC)
        canonical_job_id = str(uuid.UUID(job_id))
        if canonical_job_id != job_id:
            raise ValueError
    except (AttributeError, TypeError, ValueError) as exc:
        raise HistoryCursorError(_CURSOR_ERROR) from exc
    return normalized, canonical_job_id


def encode_history_cursor(created_at: datetime, job_id: str) -> str:
    """Return one canonical unpadded base64url cursor for a UTC job boundary."""
    normalized, canonical_job_id = _validated_values(created_at, job_id)
    payload = json.dumps(
        {
            "created_at": normalized.isoformat().replace("+00:00", "Z"),
            "job_id": canonical_job_id,
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    return f"{_CURSOR_VERSION}.{encoded}"


def decode_history_cursor(cursor: str) -> tuple[datetime, str]:
    """Decode one canonical report-history cursor or raise a stable validation error."""
    try:
        if not isinstance(cursor, str) or not 4 <= len(cursor) <= _CURSOR_MAX_LENGTH:
            raise ValueError
        version, encoded = cursor.split(".", maxsplit=1)
        if version != _CURSOR_VERSION or not encoded or not _CURSOR_TOKEN.fullmatch(encoded):
            raise ValueError
        padding = "=" * (-len(encoded) % 4)
        raw = base64.b64decode(
            encoded + padding,
            altchars=b"-_",
            validate=True,
        )
        canonical_encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
        if canonical_encoded != encoded:
            raise ValueError
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict) or set(payload) != _CURSOR_KEYS:
            raise ValueError
        created_text = payload["created_at"]
        job_id = payload["job_id"]
        if not isinstance(created_text, str) or not created_text.endswith("Z"):
            raise ValueError
        if not isinstance(job_id, str):
            raise ValueError
        created_at = datetime.fromisoformat(created_text[:-1] + "+00:00")
        normalized, canonical_job_id = _validated_values(created_at, job_id)
        if normalized.isoformat().replace("+00:00", "Z") != created_text:
            raise ValueError
    except (
        AttributeError,
        binascii.Error,
        HistoryCursorError,
        json.JSONDecodeError,
        TypeError,
        UnicodeDecodeError,
        ValueError,
    ) as exc:
        raise HistoryCursorError(_CURSOR_ERROR) from exc
    return normalized, canonical_job_id
