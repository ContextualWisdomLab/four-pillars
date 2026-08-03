from __future__ import annotations

from datetime import UTC, datetime

import pytest

from four_pillars.analysis import PracticalSkillsDraft, SynthesisDraft, generate_report
from four_pillars.calendar import calculate_chart
from four_pillars.fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from four_pillars.models import (
    BirthInput,
    Gender,
    PracticalSkill,
    ReportDocument,
    ReportSection,
)
from four_pillars.nim import NimTrace


REQUIRED = ("natal", "daewoon", "annual", "monthly", "work", "money", "relationships", "daily_rhythm")


def section(title: str) -> ReportSection:
    return ReportSection(
        title=title,
        summary="혜지 님은 계산 근거와 현실 조건을 함께 확인합니다.",
        opportunities=["구체적인 합의를 통해 신뢰와 협력을 높일 수 있습니다."],
        cautions=["혜지 님은 피로한 상태에서 결정을 서두르지 않습니다."],
        actions=["혜지 님은 담당 범위, 기한, 지원, 보상을 문서로 확인합니다."],
        examples=["회의 후 확인 메일을 보냅니다."],
        evidence=["월운 丙申"],
    )


def fixture_bundle():
    chart = calculate_chart(BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul"))
    return (
        chart,
        calculate_daewoon(chart, Gender.FEMALE, count=2),
        calculate_annual_luck(chart, 2026),
        calculate_monthly_luck(chart, 2026, 8),
    )


class FakeClient:
    def __init__(self, *, invalid_synthesis: bool = False) -> None:
        self.invalid_synthesis = invalid_synthesis
        self.calls: list[str] = []

    async def generate(self, *, system_prompt, user_payload, response_model, **kwargs):
        self.calls.append(response_model.__name__)
        trace = NimTrace(model="fake-nim", attempts=1, repairs=0, raw_content="{}")
        if response_model is ReportSection:
            return section("단계 분석"), trace
        if response_model is PracticalSkillsDraft:
            return PracticalSkillsDraft(
                practical_skills=[
                    PracticalSkill(
                        name="주간 검토",
                        purpose="다음 주의 일정과 완충 시간을 확인합니다.",
                        steps=["확정 일정을 표시합니다.", "가안 일정에 판단일을 적습니다."],
                        when_to_use="매주 금요일에 사용합니다.",
                    )
                ]
            ), trace
        if response_model is SynthesisDraft:
            summary = "시키는 대로 책임지는 사람입니다." if self.invalid_synthesis else "혜지 님은 책임 범위와 지원 조건을 확인합니다."
            return SynthesisDraft(
                executive_summary=summary,
                sections={key: section(key) for key in REQUIRED},
                disclaimer="이 보고서는 전통 명리학의 상징 자료입니다. 의학·법률·재정 판단은 실제 정보와 전문가 의견을 우선합니다.",
            ), trace
        if response_model is ReportDocument:
            fingerprint = user_payload["calculation"]["calculation_fingerprint"]
            return ReportDocument(
                subject_name="최혜지",
                title="최혜지 사주 보고서",
                executive_summary="혜지 님은 책임 범위와 지원 조건을 확인합니다.",
                calculation_fingerprint=fingerprint,
                sections={key: section(key) for key in REQUIRED},
                practical_skills=[
                    PracticalSkill(
                        name="주간 검토",
                        purpose="일정 충돌을 미리 확인합니다.",
                        steps=["캘린더를 엽니다.", "완충 시간을 확보합니다."],
                        when_to_use="매주 사용합니다.",
                    )
                ],
                disclaimer="이 보고서는 전통 명리학의 상징 자료입니다. 의학·법률·재정 판단은 실제 정보와 전문가 의견을 우선합니다.",
                generated_at=datetime.now(UTC),
                model="fake-nim",
                prompt_versions={"editorial_repair": "1.0.0"},
            ), trace
        raise AssertionError(response_model)


@pytest.mark.asyncio
async def test_generate_report_runs_all_stages_and_preserves_fingerprint() -> None:
    chart, daewoon, annual, monthly = fixture_bundle()
    client = FakeClient()
    generated = await generate_report(
        client=client,
        subject_name="최혜지",
        chart=chart,
        daewoon=daewoon,
        annual=annual,
        monthly=monthly,
        user_context="직장과 생활 계획을 설명해 주세요.",
    )
    assert generated.report.calculation_fingerprint == chart.fingerprint
    assert set(generated.report.sections) == set(REQUIRED)
    assert len(generated.report.practical_skills) == 1
    assert client.calls.count("ReportSection") == 4
    assert "SynthesisDraft" in client.calls
    assert set(generated.traces) == {
        "natal_analysis",
        "daewoon_analysis",
        "annual_analysis",
        "monthly_analysis",
        "practical_skills",
        "synthesis",
    }
    for trace in generated.traces.values():
        assert trace["prompt_version"] == "1.0.0"
        assert len(trace["prompt_sha256"]) == 64


@pytest.mark.asyncio
async def test_invalid_synthesis_receives_one_editorial_repair() -> None:
    chart, daewoon, annual, monthly = fixture_bundle()
    client = FakeClient(invalid_synthesis=True)
    generated = await generate_report(
        client=client,
        subject_name="최혜지",
        chart=chart,
        daewoon=daewoon,
        annual=annual,
        monthly=monthly,
    )
    assert "ReportDocument" in client.calls
    assert generated.report.quality_notes
    assert "시키는 대로" not in generated.report.executive_summary
    assert generated.traces["editorial_repair"]["prompt_version"] == "1.0.0"
    assert len(generated.traces["editorial_repair"]["prompt_sha256"]) == 64
