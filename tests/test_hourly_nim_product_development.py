"""Lock the hourly NVIDIA NIM OpenCode development security and product contract."""

from __future__ import annotations

import importlib.util
import os
import stat
from pathlib import Path
from types import ModuleType

import pytest

WORKFLOW = Path(".github/workflows/hourly-nim-product-development.yml")
PARSER = Path("scripts/prepare_agent_pr_message.py")
RUNBOOK = Path("docs/operations/HOURLY_NIM_PRODUCT_DEVELOPMENT.md")
DOCTORING = Path("docs/doctoring/hourly-nim-product-development.md")
ARCHITECTURE = Path("ARCHITECTURE.md")
CLAUDE = Path("CLAUDE.md")
AGENTS = Path("AGENTS.md")


def read_required(path: Path) -> str:
    """Read one required UTF-8 contract file after proving that it exists."""

    assert path.is_file(), f"required contract file is missing: {path}"
    return path.read_text(encoding="utf-8")


def load_parser_module() -> ModuleType:
    """Import the trusted pull-request metadata parser as a testable module."""

    assert PARSER.is_file(), f"required parser is missing: {PARSER}"
    spec = importlib.util.spec_from_file_location("prepare_agent_pr_message", PARSER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hourly_nim_workflow_has_an_independent_minute_47_schedule() -> None:
    """Keep deterministic minute-17 verification and NIM development separate."""

    text = read_required(WORKFLOW)

    assert 'cron: "47 * * * *"' in text
    assert "workflow_dispatch:" in text
    assert "dry_run:" in text
    assert "hourly-nim-product-development-${{ github.repository }}" in text
    assert "cancel-in-progress: false" in text
    assert "Hourly Product Quality Loop" not in text


def test_hourly_nim_workflow_uses_only_the_dedicated_model_credential() -> None:
    """Give OpenCode NVIDIA NIM access without altering reviewer credentials."""

    text = read_required(WORKFLOW)

    assert "secrets.NVIDIA_NIM_API_KEY" in text
    assert "NVIDIA_API_KEY" in text
    assert "COPILOT_GITHUB_TOKEN" not in text
    assert "CONTEXTUAL_ORCHESTRATOR_TOKEN" not in text
    assert "opencode run" in text
    assert "nvidia-nim/" in text
    assert "OPENCODE_VERSION" in text
    assert "OPENCODE_SHA256" in text
    assert "sha256sum -c" in text


def test_hourly_nim_workflow_is_pull_request_first_and_fail_closed() -> None:
    """Run the model only when PR inventory is readable and the queue is empty."""

    text = read_required(WORKFLOW)

    for token in (
        "pull_request_inventory_unavailable",
        "open_pull_request",
        "nim_api_key_unavailable",
        "maintainer_app_unavailable",
        "gh pr list",
        "--limit 1",
        "base_branch_advanced",
        "open_pull_request_after_generation",
    ):
        assert token in text
    assert text.count("gh pr create") == 1
    assert "gh pr merge" not in text
    assert "git tag" in text
    assert "gh release create" not in text


def test_hourly_nim_workflow_uses_three_isolated_runners() -> None:
    """Separate model execution, verification, and credential-bearing publication."""

    text = read_required(WORKFLOW)

    for job_name in (
        "propose_product_increment:",
        "package_product_increment:",
        "publish_product_increment:",
    ):
        assert job_name in text

    proposer = text.split("propose_product_increment:", 1)[1].split(
        "package_product_increment:", 1
    )[0]
    verifier = text.split("package_product_increment:", 1)[1].split(
        "publish_product_increment:", 1
    )[0]
    publisher = text.split("publish_product_increment:", 1)[1]

    assert "NVIDIA_NIM_API_KEY" in proposer
    assert "create-github-app-token" not in proposer
    assert "gh pr create" not in proposer
    assert "git push origin" not in proposer

    assert "NVIDIA_NIM_API_KEY" not in verifier
    assert "create-github-app-token" not in verifier
    assert "gh pr create" not in verifier
    assert "Run every release-quality gate" in verifier

    assert "NVIDIA_NIM_API_KEY" not in publisher
    assert "create-github-app-token" in publisher
    assert "gh pr create" in publisher
    assert "python -m pip install" not in publisher
    assert "pytest " not in publisher

    assert text.index("Preserve trusted metadata parser") < text.index(
        "Verify and apply immutable proposal without executing it"
    )
    assert text.index("Parse bounded untrusted pull-request metadata") < text.index(
        "Mint dedicated maintainer App token only for publication"
    )


def test_hourly_nim_workflow_binds_and_bounds_the_immutable_handoff() -> None:
    """Reject stale, oversized, mutable, symlink, and gitlink proposals."""

    text = read_required(WORKFLOW)

    for token in (
        "artifact-id",
        "artifact-digest",
        "patch_sha256",
        "changed_files",
        "diff_bytes",
        "MAX_CHANGED_FILES",
        "MAX_DIFF_BYTES",
        "120000",
        "160000",
        "git diff --cached --check",
        "git apply --check --binary",
        "retention-days: 1",
        "overwrite: false",
    ):
        assert token in text
    assert text.count("artifact-ids:") == 2
    assert text.count("workflow_run.id") == 2


def test_hourly_nim_workflow_removes_untrusted_runtime_channels() -> None:
    """Keep model and verifier processes away from GitHub mutation channels."""

    text = read_required(WORKFLOW)

    for token in (
        "-u GH_TOKEN",
        "-u GITHUB_TOKEN",
        "-u ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        "-u ACTIONS_RUNTIME_TOKEN",
        "-u ACTIONS_RESULTS_URL",
        "-u ACTIONS_CACHE_URL",
        "-u GITHUB_ENV",
        "-u GITHUB_OUTPUT",
        "-u GITHUB_PATH",
        "-u GITHUB_STATE",
        "-u GITHUB_STEP_SUMMARY",
        "timeout --kill-after",
        '"webfetch": "deny"',
        '"websearch": "deny"',
        '"external_directory": "deny"',
        '"task": "deny"',
        '"git push *": "deny"',
        '"gh *": "deny"',
    ):
        assert token in text


def test_hourly_nim_prompt_requires_commercial_and_research_quality() -> None:
    """Make each zero-queue proposal close one buyer-visible bounded gap."""

    text = read_required(WORKFLOW)

    for token in (
        "buyer-visible",
        "exactly one bounded pull request",
        "standalone",
        "modular MSA",
        "ContextualWisdomLab/.github",
        "naruon",
        "contextual-orchestrator",
        "Fugu",
        "Conductor",
        "TRINITY",
        "single-model",
        "deep multi-agent",
        "reasoning effort",
        "access lists",
        "recursive depth",
        "ablation",
        "Speed is not a priority",
        "100% production statement and branch coverage",
        "100% public docstring coverage",
        "two-word-or-longer snake_case",
        "APA 7",
        "CHANGELOG.md",
        "Do not merge",
        "Do not release",
        "Do not deploy",
    ):
        assert token.casefold() in text.casefold()


def test_fresh_verifier_runs_every_release_quality_gate() -> None:
    """Require the exact proposal to pass the repository's complete gate."""

    text = read_required(WORKFLOW)
    verifier = text.split("package_product_increment:", 1)[1].split(
        "publish_product_increment:", 1
    )[0]

    for command in (
        "python -m pip check",
        "python scripts/product_gap_audit.py",
        "ruff check .",
        "python -m compileall -q src tests scripts",
        "python scripts/check_docs.py",
        "python scripts/check_prompts.py",
        "pytest -m 'not nim_live'",
        "python -m build --no-isolation",
    ):
        assert command in verifier


def test_parser_accepts_bounded_unicode_and_writes_private_outputs(tmp_path: Path) -> None:
    """Parse one realistic Korean PR title and body without lossy conversion."""

    parser = load_parser_module()
    source = tmp_path / "PR_MESSAGE.md"
    title_path = tmp_path / "title.txt"
    body_path = tmp_path / "body.md"
    source.write_text(
        "feat: 시간별 NIM 제품 개발 루프 추가\r\n\r\n"
        "구매자가 체감하는 제품 Gap 하나를 안전하게 닫습니다.\r\n",
        encoding="utf-8",
    )

    title, body = parser.parse_pr_message(
        source,
        title_path,
        body_path,
        max_title_bytes=120,
        max_body_bytes=20_000,
    )

    assert title == "feat: 시간별 NIM 제품 개발 루프 추가"
    assert body == "구매자가 체감하는 제품 Gap 하나를 안전하게 닫습니다."
    assert title_path.read_text(encoding="utf-8") == title
    assert body_path.read_text(encoding="utf-8") == body
    assert stat.S_IMODE(title_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(body_path.stat().st_mode) == 0o600


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (b"\xff\xfe", "UTF-8"),
        (b"\nbody", "title"),
        (b"title\n\n", "body"),
        (b"title\n\nline\x00", "control"),
        ("title\n\nline\u202e".encode("utf-8"), "bidirectional"),
    ],
)
def test_parser_rejects_malformed_or_unsafe_metadata(
    tmp_path: Path,
    payload: bytes,
    message: str,
) -> None:
    """Reject malformed encoding, missing sections, controls, and bidi spoofing."""

    parser = load_parser_module()
    source = tmp_path / "PR_MESSAGE.md"
    source.write_bytes(payload)

    with pytest.raises(ValueError, match=message):
        parser.parse_pr_message(
            source,
            tmp_path / "title.txt",
            tmp_path / "body.md",
            max_title_bytes=120,
            max_body_bytes=20_000,
        )


def test_parser_enforces_utf8_byte_budgets(tmp_path: Path) -> None:
    """Measure title and body limits in bytes rather than Python characters."""

    parser = load_parser_module()
    source = tmp_path / "PR_MESSAGE.md"

    source.write_text(f"{'가' * 41}\n\nbody", encoding="utf-8")
    with pytest.raises(ValueError, match="title"):
        parser.parse_pr_message(
            source,
            tmp_path / "title.txt",
            tmp_path / "body.md",
            max_title_bytes=120,
            max_body_bytes=20_000,
        )

    source.write_text(f"title\n\n{'가' * 7}", encoding="utf-8")
    with pytest.raises(ValueError, match="body"):
        parser.parse_pr_message(
            source,
            tmp_path / "title.txt",
            tmp_path / "body.md",
            max_title_bytes=120,
            max_body_bytes=20,
        )


def test_parser_rejects_symlinks_and_non_regular_sources(tmp_path: Path) -> None:
    """Refuse metadata whose path identity can be redirected or is not a file."""

    parser = load_parser_module()
    target = tmp_path / "real.md"
    target.write_text("title\n\nbody", encoding="utf-8")
    link = tmp_path / "PR_MESSAGE.md"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks are unavailable on this platform")

    with pytest.raises(ValueError, match="regular"):
        parser.parse_pr_message(
            link,
            tmp_path / "title.txt",
            tmp_path / "body.md",
            max_title_bytes=120,
            max_body_bytes=20_000,
        )

    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(ValueError, match="regular"):
        parser.parse_pr_message(
            directory,
            tmp_path / "title.txt",
            tmp_path / "body.md",
            max_title_bytes=120,
            max_body_bytes=20_000,
        )


def test_root_agent_and_architecture_documents_explain_the_control_plane() -> None:
    """Give human and model maintainers one beginner-readable source of truth."""

    architecture = read_required(ARCHITECTURE)
    claude = read_required(CLAUDE)
    agents = read_required(AGENTS)

    for token in (
        "standalone",
        "modular MSA",
        "deterministic calculation",
        "Contextual Orchestrator",
        "NVIDIA NIM",
        "hourly",
        "Mermaid",
    ):
        assert token.casefold() in architecture.casefold()
    for token in (
        "NVIDIA_NIM_API_KEY",
        "COPILOT_GITHUB_TOKEN",
        "100%",
        "APA 7",
        "database",
        "pull request",
    ):
        assert token.casefold() in claude.casefold()
    for token in (
        "hourly",
        "OpenCode",
        "review",
        "exact-head",
        "no merge",
    ):
        assert token.casefold() in agents.casefold()


def test_operations_and_doctoring_cover_enablement_and_primary_sources() -> None:
    """Document setup, rollback, evidence boundaries, and APA 7 research."""

    runbook = read_required(RUNBOOK)
    doctoring = read_required(DOCTORING)

    for heading in (
        "## Schedule and queue behavior",
        "## Required repository configuration",
        "## Three-runner trust boundary",
        "## Failure and recovery",
        "## Disablement and rollback",
        "## Residual risks",
    ):
        assert heading in runbook
    for token in (
        "Fugu",
        "2606.21228",
        "TRINITY",
        "2512.04695",
        "Conductor",
        "2512.04388",
        "NIST SP 800-218",
        "APA 7",
        "OpenCode 1.18.13",
        "OpenCode 1.17.13",
    ):
        assert token in doctoring
