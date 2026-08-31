"""Keep the test toolchain compatible with supported Python versions."""

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pytest_asyncio_supports_python_314() -> None:
    """Require the stable pytest-asyncio line that removed legacy policy calls."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "pytest-asyncio>=1.4,<2" in project["project"]["optional-dependencies"]["dev"]
