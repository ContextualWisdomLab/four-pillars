"""Verify the reusable and idempotent GitHub release workflow contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

WORKFLOW = Path(".github/workflows/release.yml")
RELEASE_NOTES_SCRIPT = Path("scripts/release_notes.py")


def load_release_notes_module() -> ModuleType:
    """Import the release-notes script as a testable module."""
    spec = importlib.util.spec_from_file_location("release_notes", RELEASE_NOTES_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_workflow_supports_main_push_manual_and_central_reuse() -> None:
    """Validate on every supported trigger while publishing only from the main branch."""
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "push:" in text
    assert "branches: [main]" in text
    assert "workflow_dispatch:" in text
    assert "workflow_call:" in text
    assert "contents: read" in text
    assert "contents: write" in text
    assert "github.ref == 'refs/heads/main'" in text


def test_release_workflow_runs_the_complete_gate_before_publication() -> None:
    """Require all deterministic release checks and a pinned container build before release."""
    text = WORKFLOW.read_text(encoding="utf-8")

    for command in (
        "python scripts/product_gap_audit.py",
        "ruff check .",
        "python -m compileall -q src tests scripts",
        "python scripts/check_docs.py",
        "python scripts/check_prompts.py",
        "pytest -m 'not nim_live'",
        "python -m build --no-isolation",
        "docker build --tag four-pillars:release .",
    ):
        assert command in text
    assert "needs: validate" in text


def test_release_workflow_builds_versioned_notes_checksums_and_idempotent_release() -> None:
    """Create one release per package version without overwriting an existing tag."""
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "python scripts/release_notes.py" in text
    assert "SHA256SUMS" in text
    assert "gh release view" in text
    assert "gh release create" in text
    assert 'tag="v$version"' in text
    assert "--target \"$GITHUB_SHA\"" in text
    assert "NVIDIA_NIM_API_KEY" not in text


def test_release_notes_extract_exact_changelog_section() -> None:
    """Use the curated changelog section rather than generated commit prose."""
    module = load_release_notes_module()
    changelog = """# Changelog

## [Unreleased]

- future

## [0.3.0] - 2026-08-04

### Added

- modular service ports
- hourly loop

## [0.2.0] - 2026-08-03

- previous
"""

    notes = module.extract_release_notes(changelog, "0.3.0")

    assert notes.startswith("## [0.3.0] - 2026-08-04")
    assert "modular service ports" in notes
    assert "## [0.2.0]" not in notes


def test_release_notes_reject_missing_or_duplicate_versions() -> None:
    """Fail closed when the changelog cannot identify one unambiguous release section."""
    module = load_release_notes_module()

    with pytest.raises(ValueError, match="exactly one"):
        module.extract_release_notes("# Changelog\n", "0.3.0")
    with pytest.raises(ValueError, match="exactly one"):
        module.extract_release_notes(
            "## [0.3.0] - 2026-08-04\nA\n## [0.3.0] - 2026-08-05\nB\n",
            "0.3.0",
        )
