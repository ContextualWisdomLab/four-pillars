"""Fail-closed validation for autonomous termination evidence."""

from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from datetime import datetime
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
_SHA_RE = re.compile(r"[0-9a-f]{40}", re.IGNORECASE)


def _validate_revisioned_evidence(
    value: Any,
    *,
    field: str,
    expected_names: Collection[str],
    status: str,
    revision: str,
) -> None:
    """Require the independently resolved inventory at one exact revision."""
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"{field} must be a non-empty evidence map")
    if set(value) != set(expected_names):
        raise ValueError(f"{field} inventory does not match independently required names")
    for name, evidence in value.items():
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(evidence, Mapping)
            or evidence.get("status") != status
            or evidence.get("revision") != revision
        ):
            raise ValueError(f"{field} contains stale, unknown, or mismatched evidence")


def validate_final_sweep_record(
    record: Mapping[str, Any],
    *,
    expected_documents: Collection[str],
    expected_gates: Collection[str],
) -> None:
    """Reject incomplete or contradictory ``final_sweep_record_v1`` evidence."""
    missing = _REQUIRED_FIELDS.difference(record)
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")

    scope = record["scope"]
    if (
        not isinstance(scope, list)
        or not scope
        or any(not isinstance(item, str) or not item.strip() for item in scope)
    ):
        raise ValueError("scope must be a non-empty list of names")
    for field in ("protected_main_sha", "live_base_sha", "source_head_sha"):
        identity = record[field]
        if not isinstance(identity, str) or _SHA_RE.fullmatch(identity) is None:
            raise ValueError(f"{field} must be one exact Git SHA")
    source_head_sha = record["source_head_sha"]

    _validate_revisioned_evidence(
        record["required_documents"],
        field="required_documents",
        expected_names=expected_documents,
        status="current",
        revision=source_head_sha,
    )
    _validate_revisioned_evidence(
        record["gate_results"],
        field="gate_results",
        expected_names=expected_gates,
        status="success",
        revision=source_head_sha,
    )
    recorded_at = record["recorded_at"]
    if not isinstance(recorded_at, str):
        raise ValueError("recorded_at must be a canonical UTC timestamp")
    try:
        parsed_recorded_at = datetime.strptime(recorded_at, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValueError("recorded_at must be a canonical UTC timestamp") from exc
    if parsed_recorded_at.strftime("%Y-%m-%dT%H:%M:%SZ") != recorded_at:
        raise ValueError("recorded_at must be a canonical UTC timestamp")

    provenance = record["provenance"]
    if not isinstance(provenance, Mapping):
        raise ValueError("provenance must be a current evidence map")
    evidence_sources = provenance.get("evidence_sources")
    if (
        provenance.get("status") != "current"
        or provenance.get("source_head_sha") != source_head_sha
        or not isinstance(provenance.get("workflow"), str)
        or not provenance["workflow"].strip()
        or not isinstance(evidence_sources, list)
        or not evidence_sources
        or any(
            not isinstance(source, str) or not source.strip()
            for source in evidence_sources
        )
    ):
        raise ValueError("provenance contains stale, unknown, or incomplete evidence")

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
