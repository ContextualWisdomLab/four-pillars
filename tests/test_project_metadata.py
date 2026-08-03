from __future__ import annotations

import tomllib
from pathlib import Path


def test_package_license_metadata_matches_repository_license() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["license"] == {"file": "LICENSE"}
    assert Path("LICENSE").read_text(encoding="utf-8").startswith("MIT License")
