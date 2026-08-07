"""Parse the hourly PR steward workflow as data before GitHub executes it."""

from pathlib import Path

import yaml

WORKFLOW = Path(".github/workflows/hourly-pr-steward.yml")


def test_hourly_pr_steward_yaml_has_five_explicit_trust_zone_jobs() -> None:
    """Reject malformed YAML or missing proposal/verification authority boundaries."""

    document = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    assert isinstance(document, dict)
    assert set(document["on"]) == {"workflow_dispatch", "workflow_call", "schedule"}
    assert set(document["jobs"]) == {
        "inspect_pull_request",
        "propose_repair",
        "verify_repair",
        "publish_repair",
        "queue_governed_merge",
    }
    assert document["concurrency"]["cancel-in-progress"] == "false"
    assert document["on"]["schedule"] == [{"cron": "7 * * * *"}]
