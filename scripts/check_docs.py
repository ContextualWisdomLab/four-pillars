"""Validate that required project documentation is complete and publishable."""

from __future__ import annotations

from pathlib import Path

REQUIRED = (
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "docs/product-technical-gap-baseline.md",
    "docs/product/PRD.md",
    "docs/technical/TRD.md",
    "docs/technical/CALCULATION.md",
    "docs/technical/API.md",
    "docs/technical/MODULARITY.md",
    "docs/operations/NIM.md",
    "docs/operations/RUNBOOK.md",
    "docs/operations/HOURLY_PRODUCT_LOOP.md",
    "docs/standards/REFERENCES.md",
    "docs/standards/TRACEABILITY.md",
    "docs/uml/architecture.md",
    "docs/uml/domain.puml",
    "docs/adr/0001-deterministic-core-and-nim-boundary.md",
    "docs/adr/0002-nvidia-nim.md",
    "docs/adr/0003-explicit-contextual-orchestrator-backend.md",
)
FORBIDDEN = ("TBD", "TODO", "implement later", "fill in details")
STANDARDS_TOKENS = {
    "docs/standards/REFERENCES.md": (
        "APA 7th",
        "ISO/IEC Standard No. 25010:2023",
        "ISO/IEC Standard No. 42001:2023",
        "ISO/IEC Standard No. 23894:2023",
        "NIST AI 600-1",
        "RFC 9457",
        "W3C recommendation",
        "10.18653/v1/2024.emnlp-main.427",
        "10.18653/v1/2024.emnlp-main.474",
    ),
    "docs/standards/TRACEABILITY.md": (
        "ContextualOrchestratorClient",
        "StructuredGenerationClient",
        "NVIDIA_NIM_API_KEY",
        "CONTEXTUAL_ORCHESTRATOR_TOKEN",
        "100% statement and branch coverage",
        "traditional interpretation",
    ),
}


def main() -> None:
    """Fail when required doctoring is missing, too short, or incomplete."""
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
    for name, tokens in STANDARDS_TOKENS.items():
        path = Path(name)
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        for token in tokens:
            if token not in text:
                failures.append(f"missing standards token {token!r}: {name}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Validated {len(REQUIRED)} documents")


if __name__ == "__main__":
    main()
