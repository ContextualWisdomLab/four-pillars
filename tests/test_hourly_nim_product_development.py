"""Lock the hourly NVIDIA NIM OpenCode development security contract."""

from __future__ import annotations

import importlib.util
import stat
from pathlib import Path
from types import ModuleType

import pytest

WORKFLOW = Path(".github/workflows/hourly-nim-product-development.yml")
PARSER = Path("scripts/prepare_agent_pr_message.py")
RUNBOOK = Path("docs/operations/HOURLY_NIM_PRODUCT_DEVELOPMENT.md")
DOCTORING = Path("docs/doctoring/hourly-nim-opencode-development.md")


def _text(path: Path) -> str:
    """Return one required UTF-8 contract file."""

    assert path.is_file(), f"required contract file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _parser_module() -> ModuleType:
    """Load the trusted pull-request metadata parser."""

    assert PARSER.is_file()
    spec = importlib.util.spec_from_file_location("prepare_agent_pr_message", PARSER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hourly_workflow_schedule_credentials_and_queue_gate() -> None:
    """Run at minute 47 with NIM only and fail closed around PR inventory."""

    text = _text(WORKFLOW)
    for token in (
        'cron: "47 * * * *"',
        "workflow_dispatch:",
        "dry_run:",
        "hourly-nim-product-development-${{ github.repository }}",
        "cancel-in-progress: false",
        "secrets.NVIDIA_NIM_API_KEY",
        "{env:NVIDIA_NIM_API_KEY}",
        "OPENCODE_VERSION",
        "OPENCODE_SHA256",
        "sha256sum -c",
        "pull_request_inventory_unavailable",
        "open_pull_request",
        "nim_api_key_unavailable",
        "maintainer_app_unavailable",
        "base_branch_advanced",
        "open_pull_request_after_generation",
    ):
        assert token in text
    assert "COPILOT_GITHUB_TOKEN" not in text
    assert "CONTEXTUAL_ORCHESTRATOR_TOKEN" not in text
    assert text.count("gh pr create") == 1
    assert "gh pr merge" not in text
    assert "gh release create" not in text


def test_hourly_workflow_separates_three_runner_trust_boundaries() -> None:
    """Separate model execution, verification, and late publication authority."""

    text = _text(WORKFLOW)
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
    assert "NVIDIA_NIM_API_KEY" not in verifier
    assert "create-github-app-token" not in verifier
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


def test_hourly_workflow_binds_artifacts_and_strips_runtime_channels() -> None:
    """Bind the patch exactly and remove untrusted GitHub mutation channels."""

    text = _text(WORKFLOW)
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
        '"git tag *": "deny"',
        '"gh *": "deny"',
    ):
        assert token in text
    assert text.count("artifact-ids:") == 2
    assert text.count("workflow_run.id") == 2


def test_hourly_prompt_and_verifier_keep_commercial_quality_gates() -> None:
    """Require one buyer gap, research-grounded orchestration, and full checks."""

    text = _text(WORKFLOW)
    normalized = " ".join(text.casefold().split())
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
        assert token.casefold() in normalized

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


def test_parser_accepts_unicode_and_owner_only_outputs(tmp_path: Path) -> None:
    """Parse realistic Korean metadata and protect trusted output files."""

    parser = _parser_module()
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
    assert stat.S_IMODE(title_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(body_path.stat().st_mode) == 0o600


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (bytes((255, 254)), "UTF-8"),
        (b"\nbody", "title"),
        (b"title\n\n", "body"),
        (b"title\n\nline" + bytes((0,)), "control"),
        ("title\n\nline\u202e".encode(), "bidirectional"),
    ],
)
def test_parser_rejects_malformed_or_spoofed_metadata(
    tmp_path: Path,
    payload: bytes,
    message: str,
) -> None:
    """Reject malformed encoding, missing sections, controls, and bidi text."""

    parser = _parser_module()
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


def test_parser_enforces_byte_budgets_and_regular_files(tmp_path: Path) -> None:
    """Reject byte-limit violations, symlinks, and directories."""

    parser = _parser_module()
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

    target = tmp_path / "real.md"
    target.write_text("title\n\nbody", encoding="utf-8")
    link = tmp_path / "link.md"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks are unavailable on this platform")
    for invalid_source in (link, tmp_path):
        with pytest.raises(ValueError, match="regular"):
            parser.parse_pr_message(
                invalid_source,
                tmp_path / "title.txt",
                tmp_path / "body.md",
                max_title_bytes=120,
                max_body_bytes=20_000,
            )


def test_root_and_operational_documents_explain_the_control_plane() -> None:
    """Keep agent, architecture, operations, and APA evidence understandable."""

    architecture = _text(Path("ARCHITECTURE.md"))
    claude = _text(Path("CLAUDE.md"))
    agents = _text(Path("AGENTS.md"))
    runbook = _text(RUNBOOK)
    doctoring = _text(DOCTORING)

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
    for token in ("hourly", "OpenCode", "review", "exact-head", "no merge"):
        assert token.casefold() in agents.casefold()
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
        "TRINITY",
        "2512.04695",
        "Conductor",
        "2512.04388",
        "NIST SP 800-218",
        "APA 7",
        "1.18.13",
        "1.17.13",
    ):
        assert token in doctoring
