from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from four_pillars.calendar import calculate_chart
from four_pillars.fortune import calculate_daewoon, calculate_monthly_luck
from four_pillars.jobs import JobStore
from four_pillars.models import BirthInput, Gender
from four_pillars.quality import validate_report
from four_pillars.settings import Settings

from test_quality import valid_report


def test_non_sqlite_database_url_is_rejected() -> None:
    settings = Settings(database_url="postgresql://example/test")
    with pytest.raises(ValueError, match="sqlite"):
        _ = settings.sqlite_path


def test_job_retention_purges_only_old_terminal_rows(tmp_path: Path) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")
    old = store.create({"kind": "old"})
    store.claim_next()
    store.fail(old.id, "failure")
    recent = store.create({"kind": "recent"})
    store.claim_next()
    store.fail(recent.id, "failure")

    old_timestamp = (datetime.now(UTC) - timedelta(days=45)).isoformat()
    with closing(sqlite3.connect(store.database_path)) as connection, connection:
        connection.execute("UPDATE report_jobs SET updated_at=? WHERE id=?", (old_timestamp, old.id))
    assert store.purge(30) == [old.id]
    assert store.get(old.id) is None
    assert store.get(recent.id) is not None


def test_quality_gate_reports_missing_sections_vague_copy_false_authority_and_weak_disclaimer() -> None:
    report = valid_report()
    report.sections.pop("money")
    report.executive_summary = "현재 상황은 만세력 앱을 근거로 확정합니다."
    report.disclaimer = "참고용입니다."
    codes = {issue.code for issue in validate_report(report, "a" * 64)}
    assert {"missing_sections", "vague_copy", "false_authority", "weak_disclaimer"} <= codes


def test_invalid_daewoon_count_and_month_are_rejected() -> None:
    chart = calculate_chart(BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul"))
    with pytest.raises(ValueError, match="count"):
        calculate_daewoon(chart, Gender.FEMALE, count=0)
    with pytest.raises(ValueError, match="month"):
        calculate_monthly_luck(chart, 2026, 13)
