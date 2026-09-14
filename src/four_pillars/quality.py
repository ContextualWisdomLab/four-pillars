"""Reject ungrounded, unsafe, incomplete, or editorially weak report documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

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
_WITHIN_ONE_SENTENCE = r"[^.!?。！？]*"  # noqa: RUF001 - CJK full stop and marks are the terminators Korean copy uses
"""Match forward inside one reader-visible string without crossing punctuation."""

CERTAINTY_PATTERNS = (
    re.compile(rf"반드시 {_WITHIN_ONE_SENTENCE}(발생|된다|합니다)"),
    re.compile(r"틀림없이"),
    re.compile(r"확정적으로"),
)
MEDICAL_PATTERNS = (
    re.compile(r"진단(됩니다|이다|입니다)"),
    re.compile(r"약을 (복용|중단)"),
    re.compile(r"치료를 (받아야|중단해야)"),
)
FALSE_AUTHORITY_PATTERNS = (
    re.compile(rf"만세력 앱{_WITHIN_ONE_SENTENCE}근거"),
    re.compile(rf"AI가{_WITHIN_ONE_SENTENCE}보장"),
    re.compile(rf"계산기{_WITHIN_ONE_SENTENCE}확정"),
)
PILLAR_PATTERN = re.compile(f"[{''.join(STEMS_HANJA)}][{''.join(BRANCHES_HANJA)}]")


@dataclass(frozen=True)
class QualityIssue:
    """One machine-readable report-quality violation and its document path."""

    code: str
    message: str
    path: str


class ReportQualityError(ValueError):
    """Aggregate deterministic report-quality violations into one exception."""

    def __init__(self, issues: list[QualityIssue]) -> None:
        """Store all issues and create a concise joined error message."""
        self.issues = issues
        super().__init__("; ".join(f"{issue.code}: {issue.message}" for issue in issues))


def _reader_texts(report: ReportDocument) -> list[str]:
    """Return reader-visible string values without serializing field boundaries away."""
    payload = report.model_dump(mode="json", exclude={"quality_notes"})
    texts: list[str] = []
    stack: list[Any] = [payload]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
        else:
            # Every leaf in this model dumps as a string today. Stringifying any
            # other scalar keeps the walk total, so a future non-string field is
            # scanned rather than silently skipped, and leaves no dead branch.
            texts.append(str(value))
    return texts


def validate_report(
    report: ReportDocument,
    expected_fingerprint: str,
    allowed_pillars: set[str] | None = None,
) -> list[QualityIssue]:
    """Return every deterministic grounding, safety, completeness, and copy violation."""
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
    reader_texts = _reader_texts(report)
    text = "\n".join(reader_texts)
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
        if any(pattern.search(value) for value in reader_texts):
            issues.append(QualityIssue("event_certainty", "미래 사건을 확정하는 문장이 있습니다.", "$"))
    for pattern in MEDICAL_PATTERNS:
        if any(pattern.search(value) for value in reader_texts):
            issues.append(QualityIssue("medical_claim", "의학적 진단 또는 치료 지시가 있습니다.", "$"))
    for pattern in FALSE_AUTHORITY_PATTERNS:
        if any(pattern.search(value) for value in reader_texts):
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
    """Raise ``ReportQualityError`` when deterministic validation finds any issue."""
    issues = validate_report(report, expected_fingerprint, allowed_pillars)
    if issues:
        raise ReportQualityError(issues)
