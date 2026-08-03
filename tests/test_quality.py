from __future__ import annotations

from datetime import UTC, datetime

from four_pillars.models import PracticalSkill, ReportDocument, ReportSection
from four_pillars.quality import assert_report_quality, validate_report

FINGERPRINT = "a" * 64
REQUIRED_KEYS = (
    "natal",
    "daewoon",
    "annual",
    "monthly",
    "work",
    "money",
    "relationships",
    "daily_rhythm",
)


def _section(key: str) -> ReportSection:
    summary = "가까운 관계에서는 신뢰와 협력을 구체적인 약속으로 키울 수 있습니다." if key == "relationships" else "계산 근거를 생활의 조건부 판단 기준으로 설명합니다."
    return ReportSection(
        title=key,
        summary=summary,
        opportunities=["현실적인 조건을 확인하면 안정적인 성과 가능성이 있습니다."],
        cautions=["미래 사건을 단정하지 말고 실제 자료와 대화를 먼저 확인합니다."],
        actions=["사실·영향·대안·요청 순서로 다음 행동을 기록합니다."],
        examples=["책임 범위와 권한을 문서로 합의합니다."],
        evidence=["deterministic fixture"],
    )


def valid_report() -> ReportDocument:
    return ReportDocument(
        subject_name="예시 사용자",
        title="예시 사주 보고서",
        executive_summary="전통 명리학의 상징을 현실적인 자기점검 질문으로 정리합니다.",
        calculation_fingerprint=FINGERPRINT,
        sections={key: _section(key) for key in REQUIRED_KEYS},
        practical_skills=[
            PracticalSkill(
                name="주간 검토",
                purpose="일정과 책임의 과부하를 조기에 발견합니다.",
                steps=["다음 주의 핵심 일정 세 개를 적습니다.", "전체 시간의 일부를 완충 시간으로 비워 둡니다."],
                when_to_use="업무와 관계 일정이 동시에 늘어날 때",
            )
        ],
        disclaimer=(
            "이 보고서는 전통 명리학의 상징 체계를 활용한 자기점검 자료입니다. "
            "의학·법률·재정 판단은 실제 자료와 해당 분야 전문가의 판단을 우선하십시오."
        ),
        generated_at=datetime.now(UTC),
        model="fixture",
        prompt_versions={"natal_analysis": "1.0.0"},
    )


def test_valid_report_passes_quality_gate() -> None:
    report = valid_report()
    assert validate_report(report, FINGERPRINT) == []
    assert_report_quality(report, FINGERPRINT)


def test_relationship_section_requires_constructive_possibility() -> None:
    report = valid_report()
    report.sections["relationships"].summary = "갈등과 오해를 주의해야 합니다."
    report.sections["relationships"].opportunities = ["문제가 커질 수 있습니다."]
    codes = {issue.code for issue in validate_report(report, FINGERPRINT)}
    assert "relationship_warning_only" in codes


def test_fingerprint_mismatch_is_rejected() -> None:
    codes = {issue.code for issue in validate_report(valid_report(), "b" * 64)}
    assert "fingerprint_mismatch" in codes
