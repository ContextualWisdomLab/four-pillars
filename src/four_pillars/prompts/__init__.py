from __future__ import annotations

import hashlib
from dataclasses import dataclass
from importlib.resources import files


@dataclass(frozen=True)
class PromptTemplate:
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
    return {
        name: {"version": prompt.version, "sha256": prompt.sha256}
        for name in PROMPT_NAMES
        if (prompt := load_prompt(name))
    }
