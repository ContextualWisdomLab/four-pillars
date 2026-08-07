"""Validate and canonicalize untrusted pull-request steward evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import unicodedata
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

_SCHEMA_VERSION = 1
_MAX_SOURCE_BYTES = 128_000
_MAX_TEXT_BYTES = 20_000
_MAX_ITEM_TEXT_BYTES = 4_000
_MAX_ITEMS = 100
_SHA256 = re.compile(r"^[0-9a-f]{40}$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_REF = re.compile(r"^[A-Za-z0-9._/-]{1,255}$")
_ALLOWED_REVIEW_DECISIONS = {"", "APPROVED", "CHANGES_REQUESTED", "REVIEW_REQUIRED"}
_ALLOWED_REVIEW_STATES = {"APPROVED", "CHANGES_REQUESTED", "COMMENTED", "DISMISSED"}
_ALLOWED_CHECK_STATUSES = {"queued", "in_progress", "completed", "pending"}
_ALLOWED_CHECK_CONCLUSIONS = {
    "",
    "success",
    "failure",
    "neutral",
    "cancelled",
    "skipped",
    "timed_out",
    "action_required",
    "startup_failure",
    "stale",
}
_TOP_LEVEL_KEYS = {
    "schema_version",
    "repository",
    "pull_request",
    "review_decision",
    "reviews",
    "threads",
    "checks",
}
_PR_KEYS = {
    "number",
    "title",
    "body",
    "head_ref",
    "head_sha",
    "base_ref",
    "base_sha",
    "updated_at",
}
_REVIEW_KEYS = {"author", "state", "body"}
_THREAD_KEYS = {"author", "path", "line", "body", "is_resolved"}
_CHECK_KEYS = {"name", "status", "conclusion", "details_url", "summary"}
_BIDIRECTIONAL_CONTROLS = frozenset(
    {
        "\u061c",
        "\u200e",
        "\u200f",
        "\u202a",
        "\u202b",
        "\u202c",
        "\u202d",
        "\u202e",
        "\u2066",
        "\u2067",
        "\u2068",
        "\u2069",
    }
)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    """Return a mapping or raise a stable schema error."""
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    if not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} keys must be strings")
    return value


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    """Reject missing or unknown keys in one evidence object."""
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise ValueError(f"{label} keys are invalid: missing={missing}, unknown={unknown}")


def _clean_text(value: Any, label: str, maximum_bytes: int) -> str:
    """Normalize one bounded string and reject spoofing control characters."""
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    normalized = unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    for character in normalized:
        if character in _BIDIRECTIONAL_CONTROLS:
            raise ValueError(f"{label} contains a bidirectional control character")
        if unicodedata.category(character) == "Cc" and character not in {"\n", "\t"}:
            raise ValueError(f"{label} contains an unsupported control character")
    if len(normalized.encode("utf-8")) > maximum_bytes:
        raise ValueError(f"{label} exceeds the UTF-8 byte budget")
    return normalized


def _clean_identifier(value: Any, label: str, pattern: re.Pattern[str]) -> str:
    """Return one normalized identifier that matches its allow-list pattern."""
    cleaned = _clean_text(value, label, 512)
    if not pattern.fullmatch(cleaned):
        raise ValueError(f"{label} is invalid")
    return cleaned


def _clean_sha(value: Any, label: str) -> str:
    """Return one canonical lowercase Git object identifier."""
    return _clean_identifier(value, label, _SHA256)


def _clean_positive_integer(value: Any, label: str) -> int:
    """Return one positive integer while rejecting booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _clean_optional_line(value: Any, label: str) -> int | None:
    """Return an optional positive source line number."""
    if value is None:
        return None
    return _clean_positive_integer(value, label)


def _clean_https_url(value: Any, label: str) -> str:
    """Allow only bounded HTTPS GitHub URLs without credentials or fragments."""
    cleaned = _clean_text(value, label, 2_048)
    if not cleaned:
        return ""
    parsed = urlsplit(cleaned)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in {"github.com", "api.github.com"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        raise ValueError(f"{label} must be an HTTPS GitHub URL")
    return cleaned


def _clean_items(value: Any, label: str) -> list[Mapping[str, Any]]:
    """Return a bounded list of mapping items."""
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ValueError(f"{label} must be a list")
    if len(value) > _MAX_ITEMS:
        raise ValueError(f"{label} contains too many items")
    return [_require_mapping(item, f"{label}[{index}]") for index, item in enumerate(value)]


def _validate_pull_request(value: Any) -> dict[str, Any]:
    """Validate the immutable pull-request identity and bounded metadata."""
    item = _require_mapping(value, "pull_request")
    _require_exact_keys(item, _PR_KEYS, "pull_request")
    return {
        "number": _clean_positive_integer(item["number"], "pull_request.number"),
        "title": _clean_text(item["title"], "pull_request.title", 512),
        "body": _clean_text(item["body"], "pull_request.body", _MAX_TEXT_BYTES),
        "head_ref": _clean_identifier(item["head_ref"], "pull_request.head_ref", _REF),
        "head_sha": _clean_sha(item["head_sha"], "pull_request.head_sha"),
        "base_ref": _clean_identifier(item["base_ref"], "pull_request.base_ref", _REF),
        "base_sha": _clean_sha(item["base_sha"], "pull_request.base_sha"),
        "updated_at": _clean_text(item["updated_at"], "pull_request.updated_at", 128),
    }


def _validate_reviews(value: Any) -> list[dict[str, Any]]:
    """Validate bounded submitted-review evidence."""
    reviews: list[dict[str, Any]] = []
    for index, item in enumerate(_clean_items(value, "reviews")):
        label = f"reviews[{index}]"
        _require_exact_keys(item, _REVIEW_KEYS, label)
        state = _clean_text(item["state"], f"{label}.state", 64)
        if state not in _ALLOWED_REVIEW_STATES:
            raise ValueError(f"{label}.state is invalid")
        reviews.append(
            {
                "author": _clean_text(item["author"], f"{label}.author", 256),
                "state": state,
                "body": _clean_text(item["body"], f"{label}.body", _MAX_ITEM_TEXT_BYTES),
            }
        )
    return reviews


def _validate_threads(value: Any) -> list[dict[str, Any]]:
    """Validate bounded review-thread evidence."""
    threads: list[dict[str, Any]] = []
    for index, item in enumerate(_clean_items(value, "threads")):
        label = f"threads[{index}]"
        _require_exact_keys(item, _THREAD_KEYS, label)
        if not isinstance(item["is_resolved"], bool):
            raise ValueError(f"{label}.is_resolved must be a boolean")
        threads.append(
            {
                "author": _clean_text(item["author"], f"{label}.author", 256),
                "path": _clean_text(item["path"], f"{label}.path", 1_024),
                "line": _clean_optional_line(item["line"], f"{label}.line"),
                "body": _clean_text(item["body"], f"{label}.body", _MAX_ITEM_TEXT_BYTES),
                "is_resolved": item["is_resolved"],
            }
        )
    return threads


def _validate_checks(value: Any) -> list[dict[str, Any]]:
    """Validate bounded exact-head Check-run evidence."""
    checks: list[dict[str, Any]] = []
    for index, item in enumerate(_clean_items(value, "checks")):
        label = f"checks[{index}]"
        _require_exact_keys(item, _CHECK_KEYS, label)
        status = _clean_text(item["status"], f"{label}.status", 64)
        conclusion = _clean_text(item["conclusion"], f"{label}.conclusion", 64)
        if status not in _ALLOWED_CHECK_STATUSES:
            raise ValueError(f"{label}.status is invalid")
        if conclusion not in _ALLOWED_CHECK_CONCLUSIONS:
            raise ValueError(f"{label}.conclusion is invalid")
        checks.append(
            {
                "name": _clean_text(item["name"], f"{label}.name", 512),
                "status": status,
                "conclusion": conclusion,
                "details_url": _clean_https_url(item["details_url"], f"{label}.details_url"),
                "summary": _clean_text(item["summary"], f"{label}.summary", _MAX_ITEM_TEXT_BYTES),
            }
        )
    return checks


def validate_evidence(value: Any) -> dict[str, Any]:
    """Return one strict, normalized pull-request steward evidence document."""
    document = _require_mapping(value, "evidence")
    _require_exact_keys(document, _TOP_LEVEL_KEYS, "evidence")
    if document["schema_version"] != _SCHEMA_VERSION:
        raise ValueError("schema_version is unsupported")
    repository = _clean_identifier(document["repository"], "repository", _REPOSITORY)
    decision = _clean_text(document["review_decision"], "review_decision", 64)
    if decision not in _ALLOWED_REVIEW_DECISIONS:
        raise ValueError("review_decision is invalid")
    return {
        "schema_version": _SCHEMA_VERSION,
        "repository": repository,
        "pull_request": _validate_pull_request(document["pull_request"]),
        "review_decision": decision,
        "reviews": _validate_reviews(document["reviews"]),
        "threads": _validate_threads(document["threads"]),
        "checks": _validate_checks(document["checks"]),
    }


def _read_regular_file(path: Path, maximum_bytes: int = _MAX_SOURCE_BYTES) -> bytes:
    """Read a stable regular file without following symbolic links."""
    try:
        before = path.lstat()
    except OSError as exc:
        raise ValueError("evidence source must be a readable regular file") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise ValueError("evidence source must be a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValueError("evidence source must be a readable regular file") from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("evidence source must be a regular file")
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError("evidence source identity changed while opening")
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            descriptor = -1
            payload = handle.read(maximum_bytes + 1)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if len(payload) > maximum_bytes:
        raise ValueError("evidence source exceeds the byte budget")
    return payload


def _write_private_json(path: Path, value: Mapping[str, Any]) -> None:
    """Atomically replace one canonical JSON output with owner-only permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(temporary, flags, 0o600)
    except FileExistsError:
        temporary.unlink()
        descriptor = os.open(temporary, flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n", closefd=True) as handle:
            descriptor = -1
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    os.replace(temporary, path)
    os.chmod(path, 0o600)


def prepare_evidence(source_path: Path, output_path: Path) -> dict[str, Any]:
    """Read, validate, canonicalize, and privately write steward evidence."""
    payload = _read_regular_file(Path(source_path))
    try:
        decoded = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("evidence source must be valid UTF-8") from exc
    try:
        parsed = json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise ValueError("evidence source must be valid JSON") from exc
    validated = validate_evidence(parsed)
    _write_private_json(Path(output_path), validated)
    return validated


def _parser() -> argparse.ArgumentParser:
    """Build the command-line parser for evidence preparation."""
    parser = argparse.ArgumentParser(
        description="Validate untrusted PR review/Check evidence and write canonical JSON."
    )
    parser.add_argument("source_path", type=Path)
    parser.add_argument("output_path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Prepare evidence from CLI arguments and return a stable process status."""
    arguments = _parser().parse_args(argv)
    try:
        prepare_evidence(arguments.source_path, arguments.output_path)
    except ValueError as exc:
        print(f"evidence validation failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
