from __future__ import annotations

from datetime import datetime
from pathlib import Path

import httpx
import pytest
from pydantic import BaseModel, ConfigDict, ValidationError
from test_quality import valid_report

from four_pillars.analysis import PracticalSkillsDraft, SynthesisDraft
from four_pillars.calendar import calculate_chart
from four_pillars.fortune import calculate_monthly_luck
from four_pillars.jobs import JobStore
from four_pillars.models import BirthInput, PracticalSkill, ReportSection
from four_pillars.nim import NimClient, NimError
from four_pillars.quality import validate_report
from four_pillars.service import ReportService
from four_pillars.settings import Settings


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")

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


def test_llm_response_models_forbid_unknown_fields() -> None:
    section = {
        "title": "직업",
        "summary": "요약",
        "opportunities": ["기회"],
        "cautions": ["주의"],
        "actions": ["행동"],
        "unexpected": "reject",
    }
    with pytest.raises(ValidationError):
        ReportSection.model_validate(section)

    skill = {
        "name": "주간 검토",
        "purpose": "일정을 확인합니다.",
        "steps": ["일정을 적습니다.", "완충 시간을 둡니다."],
        "when_to_use": "매주",
        "unexpected": "reject",
    }
    with pytest.raises(ValidationError):
        PracticalSkill.model_validate(skill)

    with pytest.raises(ValidationError):
        PracticalSkillsDraft.model_validate({"practical_skills": [], "unexpected": "reject"})
    with pytest.raises(ValidationError):
        SynthesisDraft.model_validate(
            {
                "executive_summary": "요약",
                "sections": {},
                "disclaimer": "유의사항",
                "unexpected": "reject",
            }
        )
