"""Load versioned report prompts and expose their immutable provenance metadata."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

# The package requires Python 3.11+, where importlib.resources.files is part of the standard library.
from importlib.resources import files  # nosemgrep


@dataclass(frozen=True)
class PromptTemplate:
    """Versioned prompt body and its SHA-256 digest."""

    name: str
    version: str
    body: str
    sha256: str


PROMPT_NAMES = (
    "natal_analysis",
    "daewoon_analysis",
    "annual_analysis",
    "monthly_analysis",
    "practical_skills",
    "synthesis",
    "editorial_repair",
    "llm_judge",
)


def load_prompt(name: str) -> PromptTemplate:
    """Load one allow-listed prompt and verify its semantic version header."""
    if name not in PROMPT_NAMES:
        raise KeyError(f"Unknown prompt: {name}")
    body = files(__package__).joinpath(f"{name}.md").read_text(encoding="utf-8")
    first_line = body.splitlines()[0]
    if not first_line.startswith("version: "):
        raise ValueError(f"Prompt {name} must start with a semantic version header")
    version = first_line.removeprefix("version: ").strip()
    digest = hashlib.sha256(body.encode()).hexdigest()
    return PromptTemplate(name=name, version=version, body=body, sha256=digest)


def prompt_manifest() -> dict[str, dict[str, str]]:
    """Return prompt versions and digests without exposing prompt bodies."""
    return {
        name: {"version": prompt.version, "sha256": prompt.sha256}
        for name in PROMPT_NAMES
        if (prompt := load_prompt(name))
    }
