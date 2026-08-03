from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .constants import BRANCHES_HANJA, FORBIDDEN_COPY, STEMS_HANJA, VAGUE_COPY
from .models import ReportDocument

REQUIRED_SECTIONS = {
    "natal",
    "daewoon",
    "annual",
    "monthly",
    "work",
    "money",
    "relationships",
    "daily_rhythm",
}
CERTAINTY_PATTERNS = (
    re.compile(r"반드시 .*(발생|된다|합니다)"),
    re.compile(r"틀림없이"),
    re.compile(r"확정적으로"),
)
MEDICAL_PATTERNS = (
    re.compile(r"진단(됩니다|이다|입니다)"),
    re.compile(r"약을 (복용|중단)"),
    re.compile(r"치료를 (받아야|중단해야)"),
)
FALSE_AUTHORITY_PATTERNS = (
    re.compile(r"만세력 앱.*근거"),
    re.compile(r"AI가.*보장"),
    re.compile(r"계산기.*확정"),
)
PILLAR_PATTERN = re.compile(f"[{''.join(STEMS_HANJA)}][{''.join(BRANCHES_HANJA)}]")


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str
    path: str


class ReportQualityError(ValueError):
    def __init__(self, issues: list[QualityIssue]) -> None:
        self.issues = issues
        super().__init__("; ".join(f"{issue.code}: {issue.message}" for issue in issues))


def _all_text(report: ReportDocument) -> str:
    # Diagnostic notes intentionally quote rejected copy. They are audit metadata,
    # not reader-visible report prose, and must not cause the repaired report to fail again.
    payload = report.model_dump(mode="json", exclude={"quality_notes"})
    return json.dumps(payload, ensure_ascii=False)


def validate_report(
    report: ReportDocument,
    expected_fingerprint: str,
    allowed_pillars: set[str] | None = None,
) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    if report.calculation_fingerprint != expected_fingerprint:
        issues.append(
            QualityIssue(
                "fingerprint_mismatch",
                "보고서의 계산 fingerprint가 원 계산과 다릅니다.",
                "calculation_fingerprint",
            )
        )
    missing = sorted(REQUIRED_SECTIONS - set(report.sections))
    if missing:
        issues.append(
            QualityIssue(
                "missing_sections",
                f"필수 장이 누락되었습니다: {', '.join(missing)}",
                "sections",
            )
        )
    for key, section in report.sections.items():
        if not section.opportunities:
            issues.append(QualityIssue("missing_opportunity", "긍정적 가능성이 없습니다.", key))
        if not section.cautions:
            issues.append(QualityIssue("missing_caution", "주의점이 없습니다.", key))
        if not section.actions:
            issues.append(QualityIssue("missing_action", "실천 행동이 없습니다.", key))
    relationship = report.sections.get("relationships")
    if relationship is not None:
        positive_terms = ("신뢰", "협력", "안정", "지원", "친밀", "합의")
        relationship_copy = " ".join([relationship.summary, *relationship.opportunities])
        if not any(term in relationship_copy for term in positive_terms):
            issues.append(
                QualityIssue(
                    "relationship_warning_only",
                    "가까운 관계 장에 신뢰·협력·안정 가능성이 구체적으로 제시되지 않았습니다.",
                    "sections.relationships",
                )
            )
    text = _all_text(report)
    if allowed_pillars is not None:
        for mentioned in sorted(set(PILLAR_PATTERN.findall(text)) - allowed_pillars):
            issues.append(
                QualityIssue(
                    "ungrounded_pillar",
                    f"계산 자료에 없는 간지가 보고서에 포함되었습니다: {mentioned}",
                    "$",
                )
            )
    for phrase in FORBIDDEN_COPY:
        if phrase in text:
            issues.append(QualityIssue("forbidden_copy", f"금지 표현이 포함되었습니다: {phrase}", "$"))
    for phrase in VAGUE_COPY:
        if phrase in text:
            issues.append(QualityIssue("vague_copy", f"지시 대상이 모호합니다: {phrase}", "$"))
    for pattern in CERTAINTY_PATTERNS:
        if pattern.search(text):
            issues.append(QualityIssue("event_certainty", "미래 사건을 확정하는 문장이 있습니다.", "$"))
    for pattern in MEDICAL_PATTERNS:
        if pattern.search(text):
            issues.append(QualityIssue("medical_claim", "의학적 진단 또는 치료 지시가 있습니다.", "$"))
    for pattern in FALSE_AUTHORITY_PATTERNS:
        if pattern.search(text):
            issues.append(QualityIssue("false_authority", "앱·AI·계산기를 권위 근거로 사용했습니다.", "$"))
    disclaimer_terms = ("전통", "상징", "의학", "법률", "재정", "실제")
    if not all(term in report.disclaimer for term in disclaimer_terms):
        issues.append(
            QualityIssue(
                "weak_disclaimer",
                "면책문이 전통 상징 해석과 현실 판단의 우선순위를 충분히 설명하지 않습니다.",
                "disclaimer",
            )
        )
    return issues


def assert_report_quality(
    report: ReportDocument,
    expected_fingerprint: str,
    allowed_pillars: set[str] | None = None,
) -> None:
    issues = validate_report(report, expected_fingerprint, allowed_pillars)
    if issues:
        raise ReportQualityError(issues)
