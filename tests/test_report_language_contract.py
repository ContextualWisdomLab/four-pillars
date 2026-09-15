"""Require the prose a Korean customer reads to actually be Korean.

Every other customer-visible property is checked before a report is published:
the required sections exist, each has an opportunity, a caution and an action,
no ungrounded 간지 appears, forbidden and vague copy is rejected, and the
disclaimer carries its required terms. Nothing checked the language.

That is not theoretical. The schema-repair turn in `nim.py` appends the pydantic
error text and the full JSON Schema, both English, to the conversation and then
asks for the complete answer again, which is a known way to pull a model's
output language across.
"""

from __future__ import annotations

import pytest
from test_quality import FINGERPRINT, valid_report

from four_pillars.quality import validate_report

CODE = "foreign_language"


def _english_body(report):
    """Replace the reader-visible prose with English, leaving identifiers alone."""
    for key, section in report.sections.items():
        section.title = key.replace("_", " ").title()
        section.summary = "This section explains the calculation as a judgement aid."
        section.opportunities = ["Confirming conditions makes a stable outcome possible."]
        section.cautions = ["Do not treat future events as settled."]
        section.actions = ["Record fact, impact, alternative, request."]
    report.executive_summary = "A self-review document from traditional symbolism."
    for skill in report.practical_skills:
        skill.name = "Weekly review"
        skill.purpose = "Detect overload early."
        skill.steps = ["Write next week's three key events."]
        skill.when_to_use = "When commitments rise together."
    return report


def test_an_english_report_is_rejected() -> None:
    """The whole body in English must not reach a Korean customer unchallenged."""
    codes = [issue.code for issue in validate_report(_english_body(valid_report()), FINGERPRINT)]

    assert CODE in codes


def test_the_korean_fixture_still_passes() -> None:
    """A report written in Korean gains nothing from this check."""
    assert validate_report(valid_report(), FINGERPRINT) == []


@pytest.mark.parametrize(
    "field",
    ["title", "summary", "opportunities", "cautions", "actions"],
)
def test_one_english_field_in_one_section_is_enough_to_fail(field: str) -> None:
    """A per-report ratio would miss this; the check is per reader-visible string."""
    report = valid_report()
    english = "This single field drifted out of Korean."
    section = report.sections["work"]
    setattr(section, field, english if field in {"title", "summary"} else [english])

    assert CODE in [issue.code for issue in validate_report(report, FINGERPRINT)]


def test_a_latin_script_customer_name_is_not_a_violation() -> None:
    """The subject's own name is theirs, not prose this product wrote."""
    report = valid_report()
    report.subject_name = "Alex Marchetti"
    report.title = f"{report.subject_name} 사주 보고서"

    assert CODE not in [issue.code for issue in validate_report(report, FINGERPRINT)]
