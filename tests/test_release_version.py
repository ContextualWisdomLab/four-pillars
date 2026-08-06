"""Verify that package, API, metadata, and changelog release versions stay aligned."""

from __future__ import annotations

import tomllib
from pathlib import Path

from four_pillars import __version__
from four_pillars.api import app

RELEASE_VERSION = "0.7.0"
RELEASE_DATE = "2026-08-06"


def test_release_version_is_consistent_across_public_surfaces() -> None:
    """Expose one release number through package metadata, Python, and FastAPI."""
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]

    assert project["version"] == RELEASE_VERSION
    assert __version__ == RELEASE_VERSION
    assert app.version == RELEASE_VERSION


def test_changelog_contains_the_current_release_and_core_capabilities() -> None:
    """Describe the shipped orchestration, governance, and release guarantees."""
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
    release_header = f"## [{RELEASE_VERSION}] - {RELEASE_DATE}"

    assert release_header in changelog
    release_section = changelog.split(release_header, 1)[1].split("\n## [", 1)[0]
    normalized = release_section.casefold()
    for capability in (
        "contextual orchestrator",
        "StructuredGenerationClient",
        "auto`, `route`, or `conduct",
        "bounded",
        "HTTPS",
        "APA 7th",
        "100% statement and branch coverage",
        "NVIDIA_NIM_API_KEY",
        "CONTEXTUAL_ORCHESTRATOR_TOKEN",
        "no silent provider fallback",
    ):
        assert capability.casefold() in normalized
