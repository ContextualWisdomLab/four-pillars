"""Specify strict cursors and deterministic report-job history pagination."""

from __future__ import annotations

import base64
import json
import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from four_pillars.history import (
    HistoryCursorError,
    decode_history_cursor,
    encode_history_cursor,
)
from four_pillars.jobs import JobStore
from four_pillars.models import JobStatus


def _cursor_payload(payload: object) -> str:
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    return f"v1.{encoded.rstrip('=')}"


def _set_job_metadata(
    database_path: Path,
    job_id: str,
    *,
    created_at: datetime,
    status: JobStatus,
) -> None:
    with closing(sqlite3.connect(database_path)) as connection, connection:
        connection.execute(
            "UPDATE report_jobs SET created_at=?, updated_at=?, status=? WHERE id=?",
            (created_at.isoformat(), created_at.isoformat(), status.value, job_id),
        )


def test_history_cursor_round_trips_utc_timestamp_and_uuid() -> None:
    created_at = datetime(2026, 8, 4, 5, 6, 7, 123456, tzinfo=UTC)
    job_id = str(uuid.uuid4())

    cursor = encode_history_cursor(created_at, job_id)

    assert cursor.startswith("v1.")
    assert "=" not in cursor
    assert decode_history_cursor(cursor) == (created_at, job_id)


def test_history_cursor_rejects_noncanonical_base64url_unused_bits() -> None:
    cursor = encode_history_cursor(
        datetime(2026, 8, 4, 5, 6, 7, 123456, tzinfo=UTC),
        str(uuid.uuid4()),
    )
    version, encoded = cursor.split(".", maxsplit=1)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    remainder = len(encoded) % 4
    assert remainder in {2, 3}
    unused_mask = 0b001111 if remainder == 2 else 0b000011
    index = alphabet.index(encoded[-1])
    assert index & unused_mask == 0
    noncanonical = encoded[:-1] + alphabet[index | 0b000001]

    with pytest.raises(HistoryCursorError, match="Invalid report-history cursor"):
        decode_history_cursor(f"{version}.{noncanonical}")


@pytest.mark.parametrize(
    "cursor",
    [
        "",
        "v1.",
        "v2.invalid",
        "v1.not%base64",
        "v1." + "A" * 300,
        "v1." + base64.urlsafe_b64encode(b"not-json").decode("ascii").rstrip("="),
        _cursor_payload(["not", "an", "object"]),
        _cursor_payload(
            {
                "created_at": "2026-08-04T05:06:07+00:00",
                "job_id": str(uuid.uuid4()),
                "extra": "forbidden",
            }
        ),
        _cursor_payload(
            {
                "created_at": "2026-08-04T14:06:07+09:00",
                "job_id": str(uuid.uuid4()),
            }
        ),
        _cursor_payload(
            {
                "created_at": 123,
                "job_id": str(uuid.uuid4()),
            }
        ),
        _cursor_payload(
            {
                "created_at": "2026-08-04T05:06:07Z",
                "job_id": 123,
            }
        ),
        _cursor_payload(
            {
                "created_at": "2026-08-04T05:06:07+00:00",
                "job_id": "not-a-uuid",
            }
        ),
        _cursor_payload(
            {
                "created_at": "2026-08-04T05:06:07.000000Z",
                "job_id": str(uuid.uuid4()),
            }
        ),
    ],
)
def test_history_cursor_rejects_noncanonical_or_invalid_input(cursor: str) -> None:
    with pytest.raises(HistoryCursorError, match="Invalid report-history cursor"):
        decode_history_cursor(cursor)


@pytest.mark.parametrize(
    ("created_at", "job_id"),
    [
        (datetime(2026, 8, 4, 5, 6, 7), str(uuid.uuid4())),
        (
            datetime(
                2026,
                8,
                4,
                14,
                6,
                7,
                tzinfo=timezone(timedelta(hours=9)),
            ),
            str(uuid.uuid4()),
        ),
        (
            datetime(2026, 8, 4, 5, 6, 7, tzinfo=UTC),
            str(uuid.uuid4()).upper(),
        ),
    ],
)
def test_history_cursor_rejects_noncanonical_encoding_values(
    created_at: datetime,
    job_id: str,
) -> None:
    with pytest.raises(HistoryCursorError, match="Invalid report-history cursor"):
        encode_history_cursor(created_at, job_id)


def test_job_history_is_stable_newest_first_without_duplicate_rows(tmp_path: Path) -> None:
    database_path = tmp_path / "report_jobs.sqlite3"
    store = JobStore(database_path)
    base = datetime(2026, 8, 4, 5, 0, tzinfo=UTC)
    jobs = [store.create({"sequence": sequence}) for sequence in range(5)]
    timestamps = [
        base,
        base + timedelta(minutes=1),
        base + timedelta(minutes=1),
        base + timedelta(minutes=2),
        base + timedelta(minutes=3),
    ]
    statuses = [
        JobStatus.QUEUED,
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.COMPLETED,
        JobStatus.RUNNING,
    ]
    for job, created_at, status in zip(jobs, timestamps, statuses, strict=True):
        _set_job_metadata(
            database_path,
            job.id,
            created_at=created_at,
            status=status,
        )

    expected = [
        job.id
        for job, _created_at in sorted(
            zip(jobs, timestamps, strict=True),
            key=lambda pair: (pair[1], pair[0].id),
            reverse=True,
        )
    ]
    first, first_cursor = store.list_jobs(limit=2)
    second, second_cursor = store.list_jobs(limit=2, cursor=first_cursor)
    third, third_cursor = store.list_jobs(limit=2, cursor=second_cursor)

    actual = [job.id for job in [*first, *second, *third]]
    assert actual == expected
    assert len(actual) == len(set(actual)) == 5
    assert first_cursor is not None
    assert second_cursor is not None
    assert third_cursor is None

    after_last = encode_history_cursor(third[-1].created_at, third[-1].id)
    empty, empty_cursor = store.list_jobs(limit=2, cursor=after_last)
    assert empty == []
    assert empty_cursor is None


def test_job_history_filters_status_across_pages_and_creates_indexes(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "report_jobs.sqlite3"
    store = JobStore(database_path)
    base = datetime(2026, 8, 4, 5, 0, tzinfo=UTC)
    completed_old = store.create({"kind": "completed-old"})
    queued = store.create({"kind": "queued"})
    completed_new = store.create({"kind": "completed-new"})
    for job, minutes, status in (
        (completed_old, 0, JobStatus.COMPLETED),
        (queued, 1, JobStatus.QUEUED),
        (completed_new, 2, JobStatus.COMPLETED),
    ):
        _set_job_metadata(
            database_path,
            job.id,
            created_at=base + timedelta(minutes=minutes),
            status=status,
        )

    first, first_cursor = store.list_jobs(limit=1, status=JobStatus.COMPLETED)
    second, second_cursor = store.list_jobs(
        limit=1,
        cursor=first_cursor,
        status=JobStatus.COMPLETED,
    )

    assert [job.id for job in first] == [completed_new.id]
    assert first_cursor is not None
    assert [job.id for job in second] == [completed_old.id]
    assert second_cursor is None
    with closing(sqlite3.connect(database_path)) as connection, connection:
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
        }
    assert "idx_report_jobs_created_id" in names
    assert "idx_report_jobs_status_created_id" in names


@pytest.mark.parametrize("limit", [0, 101])
def test_job_history_rejects_invalid_direct_repository_limits(
    tmp_path: Path,
    limit: int,
) -> None:
    store = JobStore(tmp_path / "report_jobs.sqlite3")

    with pytest.raises(ValueError, match="between 1 and 100"):
        store.list_jobs(limit=limit)
