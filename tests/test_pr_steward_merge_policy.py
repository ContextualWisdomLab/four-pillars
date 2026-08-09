"""Exercise the exact-head merge policy against real repository Check names."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path("scripts/pr_steward_decision.py")
FIXTURE = Path("tests/fixtures/pr_steward_scenarios.json")


def _module() -> ModuleType:
    """Load the standard-library decision engine without importing app code."""

    spec = importlib.util.spec_from_file_location("pr_steward_merge_policy", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _green() -> dict[str, object]:
    """Return a deep copy of the realistic fully checked exact-head fixture."""

    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return json.loads(json.dumps(document["scenarios"]["green"]))


def test_real_repository_and_reviewer_checks_allow_governed_auto_merge() -> None:
    """Do not require a formal review submission when current review Checks pass."""

    evidence = _green()

    assert evidence["pull_request"]["review_decision"] is None
    assert _module().decide_action(evidence).action == "queue_merge"


def test_each_required_check_group_is_fail_closed_when_absent() -> None:
    """Wait when any Python, container, security, SAST, or reviewer gate is absent."""

    module = _module()
    for group, aliases in module.REQUIRED_CHECK_GROUPS.items():
        evidence = _green()
        evidence["checks"] = [
            check
            for check in evidence["checks"]
            if not any(alias in check["name"].casefold() for alias in aliases)
        ]

        decision = module.decide_action(evidence)

        assert decision.action == "wait"
        assert f"required_check_missing:{group}" in decision.reasons


@pytest.mark.parametrize("conclusion", ["NEUTRAL", "SKIPPED"])
def test_required_check_neutral_or_skipped_never_counts_as_passing(conclusion: str) -> None:
    """Treat non-success required conclusions as non-passing merge evidence."""

    module = _module()
    evidence = _green()
    required_alias = module.REQUIRED_CHECK_GROUPS["python_311"][0]
    matched = False
    for check in evidence["checks"]:
        if required_alias in check["name"].casefold():
            check["status"] = "COMPLETED"
            check["conclusion"] = conclusion
            matched = True
    assert matched, "realistic fixture must contain the Python 3.11 required check"

    decision = module.decide_action(evidence)

    assert decision.action == "wait"
    assert "required_check_missing:python_311" in decision.reasons
    assert "exact_head_green" not in decision.reasons


@pytest.mark.parametrize("state", ["BLOCKED", "UNSTABLE"])
def test_blocked_or_unstable_head_waits_instead_of_queueing_merge(state: str) -> None:
    """Require a passing merge state rather than delegating known blockers to auto-merge."""

    module = _module()
    evidence = _green()
    evidence["pull_request"]["merge_state_status"] = state

    decision = module.decide_action(evidence)

    assert decision.action == "wait"
    assert "merge_state_not_queueable" in decision.reasons
    assert "exact_head_green" not in decision.reasons


def test_clean_or_has_hooks_head_can_queue_after_every_explicit_gate_passes() -> None:
    """Allow only GitHub states that already report a passing commit status."""

    module = _module()
    for state in ("CLEAN", "HAS_HOOKS"):
        evidence = _green()
        evidence["pull_request"]["merge_state_status"] = state

        assert module.decide_action(evidence).action == "queue_merge"


def test_explicit_review_required_state_waits_for_independent_review() -> None:
    """Never queue merge while GitHub explicitly reports that review is required."""

    evidence = _green()
    evidence["pull_request"]["review_decision"] = "REVIEW_REQUIRED"

    decision = _module().decide_action(evidence)

    assert decision.action == "wait"
    assert "review_required" in decision.reasons
    assert "exact_head_green" not in decision.reasons


def test_review_change_request_always_requires_repair_before_queueing() -> None:
    """Keep a reviewer veto authoritative even when every Check is successful."""

    evidence = _green()
    evidence["pull_request"]["review_decision"] = "CHANGES_REQUESTED"
    evidence["reviews"] = [
        {
            "author": "independent-reviewer",
            "state": "CHANGES_REQUESTED",
            "submitted_at": "2026-08-07T06:00:00Z",
        }
    ]

    decision = _module().decide_action(evidence)

    assert decision.action == "repair"
    assert "changes_requested" in decision.reasons
