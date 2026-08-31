from __future__ import annotations

import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from four_pillars.jobs import JobStore


def test_store_connection_context_closes_the_database(tmp_path: Path) -> None:
    """Release SQLite handles when one repository operation leaves its context."""
    store = JobStore(tmp_path / "jobs.sqlite3")

    with store._connect() as connection:
        connection.execute("SELECT 1")

    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")


class LostClaimConnection:
    def __enter__(self) -> LostClaimConnection:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, statement: str, *_: object) -> SimpleNamespace:
        if statement.startswith("SELECT id"):
            return SimpleNamespace(fetchone=lambda: {"id": "lost-race"})
        if statement.startswith("UPDATE report_jobs"):
            return SimpleNamespace(rowcount=0)
        return SimpleNamespace()


def test_claim_next_returns_none_when_the_atomic_update_loses_a_race(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")
    monkeypatch.setattr(store, "_connect", LostClaimConnection)

    assert store.claim_next() is None


def test_transition_rejects_an_unknown_job(tmp_path: Path) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")

    with pytest.raises(KeyError, match="Unknown report job"):
        store.finish("missing", tmp_path / "missing")


def test_transition_rejects_a_row_that_disappears_after_update(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")
    job = store.create({"subject_name": "disappearing"})
    monkeypatch.setattr(store, "get", lambda _: None)

    with pytest.raises(KeyError, match="after transition"):
        store.fail(job.id, "failure")
