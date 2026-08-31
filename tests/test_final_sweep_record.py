"""Executable fail-closed contracts for autonomous final-sweep evidence."""

from __future__ import annotations

import pytest

from four_pillars.final_sweep import validate_final_sweep_record

EXPECTED_DOCUMENTS = frozenset({"README.md", "ARCHITECTURE.md"})
EXPECTED_GATES = frozenset({"quality", "security"})


def record(**overrides: object) -> dict[str, object]:
    """Return one structurally complete termination record."""
    value: dict[str, object] = {
        "scope": ["four-pillars"],
        "protected_main_sha": "a" * 40,
        "live_base_sha": "a" * 40,
        "source_head_sha": "b" * 40,
        "required_documents": {
            name: {"status": "current", "revision": "b" * 40}
            for name in EXPECTED_DOCUMENTS
        },
        "gate_results": {
            name: {"status": "success", "revision": "b" * 40}
            for name in EXPECTED_GATES
        },
        "remaining_executable_work": [],
        "remaining_budget": {"can_reach_safe_stopping_point": True},
        "final_decision": "no_executable_lane",
        "recorded_at": "2026-08-31T00:00:00Z",
        "provenance": {
            "status": "current",
            "source_head_sha": "b" * 40,
            "workflow": "manual-audit",
            "evidence_sources": ["local://final-sweep"],
        },
    }
    value.update(overrides)
    return value


def validate(value: dict[str, object]) -> None:
    """Validate one record against independently resolved required evidence."""
    validate_final_sweep_record(
        value,
        expected_documents=EXPECTED_DOCUMENTS,
        expected_gates=EXPECTED_GATES,
    )


def documents(**readme_updates: str) -> dict[str, dict[str, str]]:
    """Return complete document evidence with optional README corruption."""
    value = {
        name: {"status": "current", "revision": "b" * 40}
        for name in EXPECTED_DOCUMENTS
    }
    value["README.md"].update(readme_updates)
    return value


def gates(**quality_updates: str) -> dict[str, dict[str, str]]:
    """Return complete gate evidence with optional quality corruption."""
    value = {
        name: {"status": "success", "revision": "b" * 40}
        for name in EXPECTED_GATES
    }
    value["quality"].update(quality_updates)
    return value


def test_valid_termination_decisions_are_accepted() -> None:
    """Accept only internally consistent terminal decisions."""
    validate(record())
    validate(
        record(
            remaining_executable_work=["rerun exact-head checks"],
            remaining_budget={"can_reach_safe_stopping_point": False},
            final_decision="budget_continuation",
        )
    )


@pytest.mark.parametrize(
    "invalid_record",
    [
        record(remaining_executable_work=["merge ready PR"]),
        record(final_decision="budget_continuation"),
        record(
            final_decision="budget_continuation",
            remaining_executable_work=["finish review"],
        ),
        record(final_decision="continue"),
        record(final_decision="unknown"),
    ],
)
def test_contradictory_termination_decisions_fail_closed(
    invalid_record: dict[str, object],
) -> None:
    """Reject work, budget, and decision combinations that cannot justify stopping."""
    with pytest.raises(ValueError):
        validate(invalid_record)


def test_missing_or_malformed_fields_fail_closed() -> None:
    """Reject incomplete evidence and malformed state containers."""
    missing = record()
    del missing["provenance"]
    with pytest.raises(ValueError, match="missing fields"):
        validate(missing)
    with pytest.raises(ValueError, match="remaining_executable_work"):
        validate(record(remaining_executable_work="none"))
    with pytest.raises(ValueError, match="remaining_budget"):
        validate(record(remaining_budget={}))


@pytest.mark.parametrize(
    "overrides",
    [
        {"required_documents": {"README.md": {"status": "current", "revision": "b" * 40}}},
        {"gate_results": {"quality": {"status": "success", "revision": "b" * 40}}},
    ],
)
def test_omitted_required_evidence_fails_closed(overrides: dict[str, object]) -> None:
    """Reject records that omit independently required documents or gates."""
    with pytest.raises(ValueError, match="inventory"):
        validate(record(**overrides))


def test_noncanonical_timestamp_fails_closed() -> None:
    """Reject parseable UTC timestamps without canonical zero padding."""
    with pytest.raises(ValueError, match="recorded_at"):
        validate(record(recorded_at="2026-8-1T00:00:00Z"))


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"scope": []}, "scope"),
        ({"scope": "four-pillars"}, "scope"),
        ({"protected_main_sha": "bad"}, "protected_main_sha"),
        ({"live_base_sha": "bad"}, "live_base_sha"),
        ({"source_head_sha": "bad"}, "source_head_sha"),
        ({"required_documents": {}}, "required_documents"),
        (
            {"required_documents": documents(status="stale")},
            "required_documents",
        ),
        (
            {"required_documents": documents(revision="a" * 40)},
            "required_documents",
        ),
        ({"gate_results": {}}, "gate_results"),
        *[
            (
                {"gate_results": gates(status=status)},
                "gate_results",
            )
            for status in (
                "pending",
                "queued",
                "skipped_required",
                "cancelled",
                "failed",
                "unknown",
            )
        ],
        (
            {"gate_results": gates(revision="a" * 40)},
            "gate_results",
        ),
        ({"recorded_at": "yesterday"}, "recorded_at"),
        ({"recorded_at": None}, "recorded_at"),
        ({"provenance": "unknown"}, "provenance"),
        ({"provenance": {}}, "provenance"),
        (
            {"provenance": {"status": "unknown", "source_head_sha": "b" * 40, "workflow": "audit", "evidence_sources": ["local://audit"]}},
            "provenance",
        ),
        (
            {"provenance": {"status": "current", "source_head_sha": "a" * 40, "workflow": "audit", "evidence_sources": ["local://audit"]}},
            "provenance",
        ),
    ],
)
def test_identity_and_evidence_states_fail_closed(
    overrides: dict[str, object], message: str
) -> None:
    """Reject empty, stale, non-passing, or revision-mismatched evidence."""
    with pytest.raises(ValueError, match=message):
        validate(record(**overrides))
