"""Detect Actions workflow identities that outlive their source on the default branch.

GitHub keeps a workflow registry record after its YAML file is deleted. A record
that is still ``active`` while its path is absent from the protected default
branch is an orphan identity (ContextualWisdomLab/four-pillars#33). This script
is read-only: it paginates the registry, binds the observation to a commit SHA
and timestamp, classifies every identity, and exits non-zero when an active
orphan exists or when the inventory could not be completed. It never enables,
disables, or deletes anything.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NamedTuple

EXIT_CLEAN = 0
EXIT_ORPHANS = 1
EXIT_UNRESOLVED = 2

API_ROOT = "https://api.github.com"
DYNAMIC_PREFIX = "dynamic/"
WORKFLOW_DIRECTORY = ".github/workflows"

Fetcher = Callable[[str], dict[str, Any]]


class WorkflowIdentity(NamedTuple):
    """One registry record: numeric id, repository path, and lifecycle state."""

    workflow_id: int
    path: str
    state: str


class PageReceipt(NamedTuple):
    """Evidence that one registry page was fetched: URL, HTTP status, record count."""

    url: str
    status: int
    record_count: int


class Inventory(NamedTuple):
    """Paginated registry contents plus the reason the walk stopped early, if any."""

    workflows: list[WorkflowIdentity]
    receipts: list[PageReceipt]
    unresolved_reason: str | None


class RegistryReport(NamedTuple):
    """Classified inventory bound to the default-branch SHA that defined presence."""

    default_branch_sha: str
    present_active: list[WorkflowIdentity]
    absent_active: list[WorkflowIdentity]
    absent_disabled: list[WorkflowIdentity]
    dynamic: list[WorkflowIdentity]
    other: list[WorkflowIdentity]
    receipts: list[PageReceipt]
    unresolved_reasons: list[str]

    @property
    def exit_code(self) -> int:
        """Return the process exit code the incident contract assigns to this report."""
        if self.unresolved_reasons:
            return EXIT_UNRESOLVED
        if self.absent_active:
            return EXIT_ORPHANS
        return EXIT_CLEAN


def registry_url(repository: str) -> str:
    """Return the first registry page URL for ``owner/name``."""
    return f"{API_ROOT}/repos/{repository}/actions/workflows?per_page=100"


def _next_link(link_header: str | None) -> str | None:
    if not link_header:
        return None
    match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
    return match.group(1) if match else None


def github_fetcher(token: str) -> Fetcher:
    """Build a transport that returns ``{"status", "body", "next_url"}`` and never raises."""

    def fetch(url: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:  # nosec B310
                payload = json.loads(response.read().decode("utf-8"))
                return {
                    "status": response.status,
                    "body": payload,
                    "next_url": _next_link(response.headers.get("Link")),
                }
        except urllib.error.HTTPError as error:
            error.close()
            return {"status": error.code, "body": {}, "next_url": None}

    return fetch


def inventory(fetch: Fetcher, repository: str) -> Inventory:
    """Walk every registry page; stop with a reason on the first non-200 page."""
    workflows: list[WorkflowIdentity] = []
    receipts: list[PageReceipt] = []
    url: str | None = registry_url(repository)
    while url:
        page = fetch(url)
        records = page["body"].get("workflows", []) if page["status"] == 200 else []
        receipts.append(PageReceipt(url, page["status"], len(records)))
        if page["status"] != 200:
            return Inventory(workflows, receipts, f"registry_page_status_{page['status']}")
        workflows.extend(
            WorkflowIdentity(int(record["id"]), str(record["path"]), str(record["state"])) for record in records
        )
        url = page["next_url"]
    return Inventory(workflows, receipts, None)


def classify(result: Inventory, *, present_paths: set[str], default_branch_sha: str) -> RegistryReport:
    """Split identities by presence and state using exact path comparison."""
    unresolved = [result.unresolved_reason] if result.unresolved_reason else []
    seen_ids: set[int] = set()
    seen_paths: set[str] = set()
    buckets: dict[str, list[WorkflowIdentity]] = {
        "present_active": [],
        "absent_active": [],
        "absent_disabled": [],
        "dynamic": [],
        "other": [],
    }
    for identity in result.workflows:
        if identity.workflow_id in seen_ids:
            unresolved.append(f"duplicate_workflow_id_{identity.workflow_id}")
        if identity.path in seen_paths:
            unresolved.append(f"duplicate_workflow_path_{identity.path}")
        seen_ids.add(identity.workflow_id)
        seen_paths.add(identity.path)
        if identity.path.startswith(DYNAMIC_PREFIX):
            buckets["dynamic"].append(identity)
        elif identity.path in present_paths:
            bucket = "present_active" if identity.state == "active" else "other"
            buckets[bucket].append(identity)
        elif identity.state == "active":
            buckets["absent_active"].append(identity)
        else:
            buckets["absent_disabled"].append(identity)
    return RegistryReport(
        default_branch_sha,
        buckets["present_active"],
        buckets["absent_active"],
        buckets["absent_disabled"],
        buckets["dynamic"],
        buckets["other"],
        result.receipts,
        unresolved,
    )


def _rows(title: str, identities: list[WorkflowIdentity]) -> list[str]:
    lines = [f"### {title} ({len(identities)})", ""]
    if identities:
        lines += ["| id | path | state |", "|---|---|---|"]
        lines += [f"| {i.workflow_id} | `{i.path}` | {i.state} |" for i in identities]
    else:
        lines.append("_none_")
    lines.append("")
    return lines


def render(report: RegistryReport, *, observed_at: str) -> str:
    """Render the report as Markdown with SHA, time, classification, and receipts."""
    verdict = {
        EXIT_CLEAN: "PASS",
        EXIT_ORPHANS: "FAIL: active orphan workflow identities",
        EXIT_UNRESOLVED: "UNRESOLVED: inventory incomplete",
    }[report.exit_code]
    lines = [
        "# Actions Workflow Registry Audit",
        "",
        f"- Verdict: **{verdict}**",
        f"- Default branch SHA: `{report.default_branch_sha}`",
        f"- Observed at: {observed_at}",
        "",
    ]
    for title, identities in (
        ("Present on default branch, active", report.present_active),
        ("Absent from default branch, still active (orphans)", report.absent_active),
        ("Absent from default branch, disabled", report.absent_disabled),
        ("GitHub-owned dynamic workflows", report.dynamic),
        ("Other", report.other),
    ):
        lines += _rows(title, identities)
    lines += ["### Pagination receipts", "", "| url | status | records |", "|---|---|---|"]
    lines += [f"| {r.url} | {r.status} | {r.record_count} |" for r in report.receipts]
    if report.unresolved_reasons:
        lines += ["", "### Unresolved", ""] + [f"- {r}" for r in report.unresolved_reasons]
    return "\n".join(lines) + "\n"


def present_workflow_paths(root: Path) -> set[str]:
    """List workflow file paths that exist under ``root`` on the audited tree."""
    directory = root / WORKFLOW_DIRECTORY
    return {f"{WORKFLOW_DIRECTORY}/{path.name}" for path in directory.glob("*.y*ml") if path.is_file()}


def main(argv: list[str] | None = None) -> int:
    """Run the audit from the command line and return the contract exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="owner/name of the repository")
    parser.add_argument("--root", type=Path, default=Path("."), help="checked-out tree")
    parser.add_argument("--default-branch-sha", default=os.environ.get("GITHUB_SHA", "unknown"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("UNRESOLVED: GH_TOKEN or GITHUB_TOKEN with actions:read is required")
        return EXIT_UNRESOLVED

    result = inventory(github_fetcher(token), args.repository)
    report = classify(
        result,
        present_paths=present_workflow_paths(args.root),
        default_branch_sha=args.default_branch_sha,
    )
    text = render(report, observed_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return report.exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    sys.exit(main())
