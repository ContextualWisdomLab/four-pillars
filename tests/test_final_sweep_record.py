"""Executable fail-closed contracts for autonomous final-sweep evidence."""

from __future__ import annotations

import pytest

from four_pillars.final_sweep import validate_final_sweep_record


def record(**overrides: object) -> dict[str, object]:
    """Return one structurally complete termination record."""
    value: dict[str, object] = {
        "scope": ["four-pillars"],
        "protected_main_sha": "a" * 40,
        "live_base_sha": "a" * 40,
        "source_head_sha": "b" * 40,
        "required_documents": {"README.md": "current"},
        "gate_results": {"quality": "success"},
        "remaining_executable_work": [],
        "remaining_budget": {"can_reach_safe_stopping_point": True},
        "final_decision": "no_executable_lane",
        "recorded_at": "2026-08-31T00:00:00Z",
        "provenance": {"workflow": "manual-audit"},
    }
    value.update(overrides)
    return value


def test_valid_termination_decisions_are_accepted() -> None:
    """Accept only internally consistent terminal decisions."""
    validate_final_sweep_record(record())
    validate_final_sweep_record(
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
        validate_final_sweep_record(invalid_record)


def test_missing_or_malformed_fields_fail_closed() -> None:
    """Reject incomplete evidence and malformed state containers."""
    missing = record()
    del missing["provenance"]
    with pytest.raises(ValueError, match="missing fields"):
        validate_final_sweep_record(missing)
    with pytest.raises(ValueError, match="remaining_executable_work"):
        validate_final_sweep_record(record(remaining_executable_work="none"))
    with pytest.raises(ValueError, match="remaining_budget"):
        validate_final_sweep_record(record(remaining_budget={}))
