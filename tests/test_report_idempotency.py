"""Verify safe retry semantics for report creation and hosted NIM cost control."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from four_pillars.api import app, get_service
from four_pillars.idempotency import parse_idempotency_key, request_fingerprint
from four_pillars.jobs import IdempotencyKeyReuseError, JobStore
from four_pillars.models import JobStatus
from four_pillars.service import ReportService
from four_pillars.settings import Settings, get_settings
from four_pillars.web import render_home

BIRTH = {
    "birth": "1990-06-15T08:30:00",
    "timezone": "Asia/Seoul",
    "gender": "female",
    "calendar": "solar",
    "birth_time_known": True,
    "time_basis": "civil",
    "day_boundary": "midnight",
}
REPORT = {
    "subject_name": "최혜지",
    "birth": BIRTH,
    "annual_year": 2026,
    "monthly_year": 2026,
    "monthly_month": 8,
    "user_context": "직장과 생활 계획",
}
KEY = '"8e03978e-40d5-43e8-bc93-6894a57f9324"'


def client(tmp_path: Path) -> TestClient:
    """Return an isolated API client with one durable report-job store."""
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'report_jobs.sqlite3'}",
    )
    service = ReportService(settings, JobStore(settings.sqlite_path))
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app)


def teardown_function() -> None:
    """Remove FastAPI dependency overrides after every API test."""
    app.dependency_overrides.clear()


def test_structured_idempotency_key_parsing_is_strict_and_canonical() -> None:
    """Accept the RFC structured string subset and reject ambiguous raw values."""
    assert parse_idempotency_key(KEY) == "8e03978e-40d5-43e8-bc93-6894a57f9324"
    assert parse_idempotency_key('"quoted\\\\slash\\\"mark"') == 'quoted\\slash"mark'

    for invalid in (
        "unquoted-key",
        '""',
        '"short"',
        '"unterminated',
        '"bad\\nescape"',
        '"control\ncharacter"',
        f'"{"a" * 129}"',
    ):
        with pytest.raises(ValueError, match="Idempotency-Key"):
            parse_idempotency_key(invalid)


def test_request_fingerprint_is_canonical_and_payload_sensitive() -> None:
    """Ignore mapping order while distinguishing materially different requests."""
    reordered = dict(reversed(list(REPORT.items())))
    changed = {**REPORT, "monthly_month": 9}

    assert request_fingerprint(REPORT) == request_fingerprint(reordered)
    assert request_fingerprint(REPORT) != request_fingerprint(changed)
    assert len(request_fingerprint(REPORT)) == 64


def test_store_replays_the_same_request_without_storing_the_raw_key(tmp_path: Path) -> None:
    """Return one durable job for repeated key and payload pairs."""
    database = tmp_path / "report_jobs.sqlite3"
    store = JobStore(database)
    canonical_key = parse_idempotency_key(KEY)
    key_digest = hashlib.sha256(canonical_key.encode()).hexdigest()
    fingerprint = request_fingerprint(REPORT)

    first, first_replayed = store.create_idempotent(REPORT, key_digest, fingerprint)
    second, second_replayed = store.create_idempotent(REPORT, key_digest, fingerprint)

    assert first.id == second.id
    assert first.status is JobStatus.QUEUED
    assert first_replayed is False
    assert second_replayed is True
    assert second.request_fingerprint == fingerprint
    assert second.idempotency_key_digest == key_digest
    database_bytes = database.read_bytes()
    assert canonical_key.encode() not in database_bytes


def test_store_rejects_reusing_a_key_for_a_different_payload(tmp_path: Path) -> None:
    """Protect clients from accidentally assigning one key to different reports."""
    store = JobStore(tmp_path / "report_jobs.sqlite3")
    key_digest = hashlib.sha256(parse_idempotency_key(KEY).encode()).hexdigest()
    store.create_idempotent(REPORT, key_digest, request_fingerprint(REPORT))
    changed = {**REPORT, "monthly_month": 9}

    with pytest.raises(IdempotencyKeyReuseError):
        store.create_idempotent(changed, key_digest, request_fingerprint(changed))


def test_existing_job_database_is_migrated_without_losing_queued_requests(tmp_path: Path) -> None:
    """Backfill fingerprints and add the unique idempotency index to a v0.3 database."""
    database = tmp_path / "report_jobs.sqlite3"
    now = datetime.now(UTC).isoformat()
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE report_jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                request_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                error TEXT,
                artifact_dir TEXT
            )
            """
        )
        connection.execute(
            "INSERT INTO report_jobs(id,status,request_json,created_at,updated_at) VALUES(?,?,?,?,?)",
            ("legacy-job", "queued", '{"subject_name":"legacy"}', now, now),
        )

    store = JobStore(database)
    migrated = store.get("legacy-job")
    with sqlite3.connect(database) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(report_jobs)")}
        indexes = {row[1] for row in connection.execute("PRAGMA index_list(report_jobs)")}

    assert migrated is not None
    assert migrated.request_fingerprint == request_fingerprint({"subject_name": "legacy"})
    assert migrated.idempotency_key_digest is None
    assert {"request_fingerprint", "idempotency_key_digest"} <= columns
    assert "idx_report_jobs_idempotency_key_digest" in indexes


def test_api_replays_same_payload_and_marks_the_response(tmp_path: Path) -> None:
    """Return the original job for safe POST retries without duplicate NIM work."""
    with client(tmp_path) as http:
        first = http.post("/v1/reports", json=REPORT, headers={"Idempotency-Key": KEY})
        second = http.post("/v1/reports", json=REPORT, headers={"Idempotency-Key": KEY})

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["id"] == second.json()["id"]
    assert first.headers["Idempotency-Replayed"] == "false"
    assert second.headers["Idempotency-Replayed"] == "true"


def test_api_rejects_invalid_or_reused_keys_and_keeps_header_optional(tmp_path: Path) -> None:
    """Return 400 for malformed keys, 422 for payload reuse, and preserve compatibility."""
    changed = {**REPORT, "monthly_month": 9}
    with client(tmp_path) as http:
        malformed = http.post(
            "/v1/reports",
            json=REPORT,
            headers={"Idempotency-Key": "unquoted-key"},
        )
        first = http.post("/v1/reports", json=REPORT, headers={"Idempotency-Key": KEY})
        reused = http.post("/v1/reports", json=changed, headers={"Idempotency-Key": KEY})
        without_key_one = http.post("/v1/reports", json=REPORT)
        without_key_two = http.post("/v1/reports", json=REPORT)

    assert malformed.status_code == 400
    assert first.status_code == 202
    assert reused.status_code == 422
    assert "different payload" in reused.json()["detail"]
    assert without_key_one.json()["id"] != without_key_two.json()["id"]
    assert "Idempotency-Replayed" not in without_key_one.headers


def test_browser_reuses_one_generated_key_until_enqueue_succeeds() -> None:
    """Protect browser retries and invalidate reviewed evidence after input changes."""
    page = render_home()

    assert "crypto.randomUUID()" in page
    assert "Idempotency-Key" in page
    assert "reportKey" in page
    assert "form.addEventListener('input'" in page
    assert "reportKey=null" in page


def test_api_documentation_publishes_key_syntax_fingerprint_and_expiry_policy() -> None:
    """Document the experimental IETF contract and the product's lifecycle decisions."""
    text = Path("docs/technical/API.md").read_text(encoding="utf-8")

    for phrase in (
        "Idempotency-Key",
        "structured string",
        "SHA-256",
        "same job",
        "HTTP 422",
        "deleted or purged",
        "draft-ietf-httpapi-idempotency-key-header-07",
    ):
        assert phrase in text
