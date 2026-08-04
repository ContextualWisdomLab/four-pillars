"""Validate that required project documentation is complete and publishable."""

from __future__ import annotations

from pathlib import Path

REQUIRED = (
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "docs/product/PRD.md",
    "docs/technical/TRD.md",
    "docs/technical/CALCULATION.md",
    "docs/technical/API.md",
    "docs/operations/NIM.md",
    "docs/operations/RUNBOOK.md",
    "docs/uml/architecture.md",
    "docs/uml/domain.puml",
    "docs/adr/0001-deterministic-core-and-nim-boundary.md",
    "docs/adr/0002-nvidia-nim.md",
)
FORBIDDEN = ("TBD", "TODO", "implement later", "fill in details")


def main() -> None:
    """Fail when a required document is missing, too short, or contains placeholders."""
    failures: list[str] = []
    for name in REQUIRED:
        path = Path(name)
        if not path.is_file():
            failures.append(f"missing: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.strip()) < 120:
            failures.append(f"too short: {name}")
        for token in FORBIDDEN:
            if token in text:
                failures.append(f"placeholder {token!r}: {name}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Validated {len(REQUIRED)} documents")


if __name__ == "__main__":
    main()
