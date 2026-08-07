"""Exercise the exact-head merge policy against real repository Check names."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

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


def test_blocked_or_unstable_head_may_queue_but_never_bypass_governance() -> None:
    """Let GitHub auto-merge wait on residual branch rules after exact checks pass."""

    module = _module()
    for state in ("BLOCKED", "UNSTABLE", "HAS_HOOKS"):
        evidence = _green()
        evidence["pull_request"]["merge_state_status"] = state

        assert module.decide_action(evidence).action == "queue_merge"


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
