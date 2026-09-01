from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from four_pillars.jobs import JobStore


class LostClaimConnection:
    def __enter__(self) -> LostClaimConnection:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, statement: str, *_: object) -> SimpleNamespace:
        if statement.strip().startswith("SELECT report_job_id"):
            return SimpleNamespace(fetchone=lambda: {"report_job_id": "lost-race"})
        if statement.strip().startswith("UPDATE report_jobs"):
            return SimpleNamespace(rowcount=0)
        return SimpleNamespace()


def test_claim_next_returns_none_when_the_atomic_update_loses_a_race(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    report_job_store = JobStore(tmp_path / "jobs.sqlite3")
    monkeypatch.setattr(report_job_store, "_connect", LostClaimConnection)

    assert report_job_store.claim_next() is None


def test_transition_rejects_an_unknown_job(tmp_path: Path) -> None:
    report_job_store = JobStore(tmp_path / "jobs.sqlite3")

    with pytest.raises(KeyError, match="Unknown report job"):
        report_job_store.finish("missing", tmp_path / "missing")


def test_transition_rejects_a_row_that_disappears_after_update(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    report_job_store = JobStore(tmp_path / "jobs.sqlite3")
    report_job = report_job_store.create({"subject_name": "disappearing"})
    monkeypatch.setattr(report_job_store, "get", lambda _: None)

    with pytest.raises(KeyError, match="after transition"):
        report_job_store.fail(report_job.report_job_id, "failure")
