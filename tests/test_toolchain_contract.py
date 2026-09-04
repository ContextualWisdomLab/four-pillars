"""Keep the test toolchain compatible with supported Python versions."""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pytest_asyncio_supports_python_314() -> None:
    """Require the stable pytest-asyncio line that removed legacy policy calls."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "pytest-asyncio>=1.4,<2" in project["project"]["optional-dependencies"]["dev"]

    lock = (ROOT / "requirements/ci.txt").read_text(encoding="utf-8")
    locked_version = re.search(r"(?m)^pytest-asyncio==(\d+)\.(\d+)\.(\d+)", lock)
    assert locked_version is not None
    assert (1, 4) <= tuple(map(int, locked_version.groups())) < (2, 0)

    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for python_version in ("3.11", "3.12", "3.13", "3.14"):
        assert f"'{python_version}'" in workflow
