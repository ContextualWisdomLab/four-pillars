"""Keep the copy-safety patterns inside the sentence they are judging.

``validate_report`` searches one JSON serialization of the whole document, so a
pattern written with ``.*`` reaches from a word in one section to a word in a
different section thousands of characters away. The three patterns that use a
wildcard therefore fired on text that says the opposite of what they detect,
and a failure here is not cosmetic: it costs an editorial repair generation and
then fails the customer's job outright when the repaired copy hedges again.
"""

from __future__ import annotations

import pytest
from test_quality import FINGERPRINT, valid_report

from four_pillars.quality import validate_report


def _codes(report) -> list[str]:
    return [issue.code for issue in validate_report(report, FINGERPRINT)]


def test_a_hedge_that_denies_certainty_is_not_a_certainty_claim() -> None:
    """The most responsible sentence a fortune report can carry must pass."""
    report = valid_report()
    report.sections["natal"].cautions = [
        "반드시 그렇게 되는 것은 아니므로 실제 자료를 먼저 확인하십시오."
    ]

    assert "event_certainty" not in _codes(report)


def test_a_neutral_mention_of_an_almanac_app_is_not_false_authority() -> None:
    """Naming a tool is not citing it as authority, even when 근거 appears later."""
    report = valid_report()
    report.executive_summary = "이 결과는 만세력 앱으로도 확인할 수 있습니다."

    assert "false_authority" not in _codes(report)


def test_two_sentences_in_one_field_do_not_combine_into_a_claim() -> None:
    """A sentence boundary ends the match, so separate statements stay separate."""
    report = valid_report()
    report.sections["work"].cautions = [
        "반드시 확인하십시오. 조건이 갖추어지면 변화가 발생합니다."
    ]

    assert "event_certainty" not in _codes(report)


@pytest.mark.parametrize(
    ("field", "text", "code"),
    [
        ("natal", "반드시 큰 변화가 발생합니다.", "event_certainty"),
        ("natal", "이 시기에는 반드시 승진이 된다.", "event_certainty"),
        ("work", "만세력 앱이 이 해석의 유일한 근거입니다.", "false_authority"),
        ("work", "AI가 이 결과를 보장합니다.", "false_authority"),
        ("money", "계산기가 이 시기를 확정합니다.", "false_authority"),
    ],
)
def test_a_real_violation_in_one_sentence_is_still_rejected(
    field: str, text: str, code: str
) -> None:
    """Narrowing the window must not weaken what the gate exists to catch."""
    report = valid_report()
    report.sections[field].cautions = [text]

    assert code in _codes(report)
