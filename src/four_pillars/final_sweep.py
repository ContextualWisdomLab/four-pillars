"""Fail-closed validation for autonomous termination evidence."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_REQUIRED_FIELDS = frozenset(
    {
        "scope",
        "protected_main_sha",
        "live_base_sha",
        "source_head_sha",
        "required_documents",
        "gate_results",
        "remaining_executable_work",
        "remaining_budget",
        "final_decision",
        "recorded_at",
        "provenance",
    }
)


def validate_final_sweep_record(record: Mapping[str, Any]) -> None:
    """Reject incomplete or contradictory ``final_sweep_record_v1`` evidence."""
    missing = _REQUIRED_FIELDS.difference(record)
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")

    work = record["remaining_executable_work"]
    if not isinstance(work, list):
        raise ValueError("remaining_executable_work must be a list")
    budget = record["remaining_budget"]
    if not isinstance(budget, Mapping) or not isinstance(
        budget.get("can_reach_safe_stopping_point"), bool
    ):
        raise ValueError(
            "remaining_budget must declare can_reach_safe_stopping_point"
        )

    decision = record["final_decision"]
    if decision == "no_executable_lane":
        if work:
            raise ValueError("no_executable_lane requires no executable work")
        return
    if decision == "budget_continuation":
        if not work or budget["can_reach_safe_stopping_point"] is not False:
            raise ValueError(
                "budget_continuation requires work and insufficient safe-stop budget"
            )
        return
    raise ValueError("termination decision must be budget_continuation or no_executable_lane")
