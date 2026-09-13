"""Verify the read-only Actions workflow-registry recurrence detector."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

AUDIT_SCRIPT = Path("scripts/workflow_registry_audit.py")
WORKFLOW = Path(".github/workflows/hourly-product-loop.yml")


@pytest.fixture(scope="module")
def registry_audit() -> ModuleType:
    """Load the audit script as a module without executing its CLI."""
    spec = importlib.util.spec_from_file_location("workflow_registry_audit", AUDIT_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _page(*workflows: tuple[int, str, str], next_url: str | None = None) -> dict:
    return {
        "status": 200,
        "body": {
            "workflows": [
                {"id": workflow_id, "path": path, "state": state, "name": path}
                for workflow_id, path, state in workflows
            ]
        },
        "next_url": next_url,
    }


def _fetcher(pages: dict[str, dict]):
    calls: list[str] = []

    def fetch(url: str) -> dict:
        calls.append(url)
        return pages[url]

    fetch.calls = calls  # type: ignore[attr-defined]
    return fetch


def test_inventory_follows_every_link_page_and_records_receipts(
    registry_audit: ModuleType,
) -> None:
    """Truncated pagination must be followed to the end and each page receipted."""
    first = registry_audit.registry_url("owner/repo")
    fetch = _fetcher(
        {
            first: _page((1, ".github/workflows/ci.yml", "active"), next_url="p2"),
            "p2": _page((2, ".github/workflows/gone.yml", "active")),
        }
    )

    result = registry_audit.inventory(fetch, "owner/repo")

    assert [entry.workflow_id for entry in result.workflows] == [1, 2]
    assert [receipt.url for receipt in result.receipts] == [first, "p2"]
    assert all(receipt.status == 200 for receipt in result.receipts)
    assert fetch.calls == [first, "p2"]


@pytest.mark.parametrize("status", [403, 404, 500, 503])
def test_transient_or_permission_failures_are_unresolved_not_clean(registry_audit: ModuleType, status: int) -> None:
    """A 403/404/5xx page must never be reported as a clean inventory."""
    first = registry_audit.registry_url("owner/repo")
    fetch = _fetcher({first: {"status": status, "body": {"message": "nope"}, "next_url": None}})

    result = registry_audit.inventory(fetch, "owner/repo")

    assert result.unresolved_reason == f"registry_page_status_{status}"
    assert result.workflows == []
    report = registry_audit.classify(result, present_paths=set(), default_branch_sha="abc")
    assert report.exit_code == registry_audit.EXIT_UNRESOLVED


def test_classification_flags_only_active_orphans(registry_audit: ModuleType) -> None:
    """Absent-but-disabled, present, and dynamic identities are not orphans."""
    first = registry_audit.registry_url("owner/repo")
    fetch = _fetcher(
        {
            first: _page(
                (10, ".github/workflows/ci.yml", "active"),
                (11, ".github/workflows/one-shot.yml", "disabled_manually"),
                (12, ".github/workflows/deleted-helper.yml", "active"),
                (13, "dynamic/github-code-scanning/codeql", "active"),
                (14, ".github/workflows/CI.yml", "active"),
            )
        }
    )
    result = registry_audit.inventory(fetch, "owner/repo")

    report = registry_audit.classify(result, present_paths={".github/workflows/ci.yml"}, default_branch_sha="abc")

    assert [entry.workflow_id for entry in report.present_active] == [10]
    assert [entry.workflow_id for entry in report.absent_disabled] == [11]
    # Path comparison is exact: a case variant is not the present file.
    assert [entry.workflow_id for entry in report.absent_active] == [12, 14]
    assert [entry.workflow_id for entry in report.dynamic] == [13]
    assert report.exit_code == registry_audit.EXIT_ORPHANS


def test_duplicate_identity_or_reused_path_is_unresolved(registry_audit: ModuleType) -> None:
    """A workflow id or path seen twice across pages is inconsistent, not clean."""
    first = registry_audit.registry_url("owner/repo")
    fetch = _fetcher(
        {
            first: _page((1, ".github/workflows/ci.yml", "active"), next_url="p2"),
            "p2": _page((1, ".github/workflows/renamed.yml", "active")),
        }
    )
    result = registry_audit.inventory(fetch, "owner/repo")

    report = registry_audit.classify(result, present_paths={".github/workflows/ci.yml"}, default_branch_sha="abc")

    assert report.exit_code == registry_audit.EXIT_UNRESOLVED
    assert "duplicate_workflow_id_1" in report.unresolved_reasons


def test_report_binds_sha_time_and_receipts(registry_audit: ModuleType, tmp_path: Path) -> None:
    """The rendered report carries every field the incident contract requires."""
    first = registry_audit.registry_url("owner/repo")
    fetch = _fetcher({first: _page((7, ".github/workflows/ci.yml", "active"))})
    result = registry_audit.inventory(fetch, "owner/repo")
    report = registry_audit.classify(result, present_paths={".github/workflows/ci.yml"}, default_branch_sha="deadbeef")

    text = registry_audit.render(report, observed_at="2026-09-13T00:00:00Z")

    assert "`deadbeef`" in text
    assert "2026-09-13T00:00:00Z" in text
    assert "| 7 | `.github/workflows/ci.yml` | active |" in text
    assert first in text and "200" in text
    assert report.exit_code == registry_audit.EXIT_CLEAN


def test_main_reads_token_from_environment_and_writes_output(
    registry_audit: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI needs a token, resolves the present paths from the tree, and writes the report."""
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    assert registry_audit.main(["--repository", "owner/repo"]) == registry_audit.EXIT_UNRESOLVED

    first = registry_audit.registry_url("owner/repo")
    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setattr(
        registry_audit,
        "github_fetcher",
        lambda token: _fetcher({first: _page((1, ".github/workflows/ci.yml", "active"))}),
    )
    output = tmp_path / "registry.md"
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")

    code = registry_audit.main(
        [
            "--repository",
            "owner/repo",
            "--root",
            str(tmp_path),
            "--default-branch-sha",
            "cafe",
            "--output",
            str(output),
        ]
    )

    assert code == registry_audit.EXIT_CLEAN
    assert "`cafe`" in output.read_text(encoding="utf-8")


def test_github_fetcher_maps_http_errors_and_link_headers(registry_audit: ModuleType) -> None:
    """The real transport returns status, JSON body, and the rel=next link without raising."""
    import httpx

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token"
        if request.url.path == "/next":
            return httpx.Response(403, json={"message": "forbidden"})
        return httpx.Response(
            200,
            json={"workflows": []},
            headers={"Link": '<https://api.github.com/next>; rel="next"'},
        )

    fetch = registry_audit.github_fetcher("token", transport=httpx.MockTransport(handler))

    first = fetch("https://api.github.com/repos/o/r/actions/workflows?per_page=100")
    assert first["status"] == 200
    assert first["next_url"] == "https://api.github.com/next"
    assert fetch("https://api.github.com/next")["status"] == 403


@pytest.mark.parametrize(
    "url",
    ["file:///etc/passwd", "http://api.github.com/x", "https://evil.example/api.github.com/"],
)
def test_github_fetcher_refuses_non_github_api_urls(registry_audit: ModuleType, url: str) -> None:
    """Only https://api.github.com/ URLs are ever requested; anything else is unresolved."""
    import httpx

    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover - must not run
        raise AssertionError(f"unexpected request to {request.url}")

    fetch = registry_audit.github_fetcher("token", transport=httpx.MockTransport(handler))

    page = fetch(url)

    assert page["status"] == registry_audit.STATUS_REFUSED_URL
    assert page["next_url"] is None
    result = registry_audit.inventory(lambda _url: page, "owner/repo")
    assert result.unresolved_reason == f"registry_page_status_{registry_audit.STATUS_REFUSED_URL}"


def test_hourly_loop_runs_the_registry_audit_with_actions_read_only() -> None:
    """The minute-17 sentinel runs the detector read-only with the workflow token."""
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "python scripts/workflow_registry_audit.py" in text
    assert "actions: read" in text
    assert "actions: write" not in text
