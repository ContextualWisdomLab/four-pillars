from __future__ import annotations

from datetime import datetime
from pathlib import Path

import httpx
import pytest
from pydantic import BaseModel

from four_pillars.calendar import calculate_chart
from four_pillars.fortune import calculate_monthly_luck
from four_pillars.jobs import JobStore
from four_pillars.models import BirthInput
from four_pillars.nim import NimClient, NimError
from four_pillars.quality import validate_report
from four_pillars.service import ReportService
from four_pillars.settings import Settings

from test_quality import valid_report


class Answer(BaseModel):
    value: str


def test_january_monthly_luck_uses_previous_year_stem_before_li_chun() -> None:
    chart = calculate_chart(BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul"))
    january = calculate_monthly_luck(chart, 2026, 1)
    assert january.pillar.hanja == "己丑"
    assert january.starts_at.month == 1
    assert january.ends_at.month == 2


def test_quality_gate_rejects_unsupplied_sexagenary_pillar() -> None:
    report = valid_report()
    report.sections["monthly"].evidence = ["월운 甲子"]
    issues = validate_report(report, "a" * 64, allowed_pillars={"丙申"})
    assert "ungrounded_pillar" in {issue.code for issue in issues}


@pytest.mark.asyncio
async def test_zero_nim_retries_means_one_total_http_attempt() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, text="unavailable")

    settings = Settings(
        nvidia_api_key="key",
        nim_base_url="https://nim.test/v1",
        nim_model="model",
        nim_max_retries=0,
        nim_max_schema_repairs=0,
    )
    async with NimClient(settings, transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NimError, match="after retries"):
            await client.generate(system_prompt="JSON", user_payload={}, response_model=Answer)
    assert calls == 1


def test_artifact_reader_rejects_database_path_outside_configured_root(tmp_path: Path) -> None:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    store = JobStore(settings.sqlite_path)
    service = ReportService(settings, store)
    job = store.create({"subject_name": "test"})
    store.claim_next()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "report.json").write_text('{"sensitive":true}', encoding="utf-8")
    store.finish(job.id, outside)
    with pytest.raises(FileNotFoundError):
        service.artifact(job.id, "report.json")
