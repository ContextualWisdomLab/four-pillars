"""Validate versioned prompt metadata and mandatory trust-boundary language."""

from __future__ import annotations

import re

from four_pillars.prompts import PROMPT_NAMES, load_prompt

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
REQUIRED_PHRASES = ("Immutable", "Output")


def main() -> None:
    """Fail when a committed AI prompt violates the repository prompt contract."""
    failures: list[str] = []
    for name in PROMPT_NAMES:
        prompt = load_prompt(name)
        if not SEMVER.fullmatch(prompt.version):
            failures.append(f"invalid version: {name}={prompt.version}")
        if len(prompt.body) < 300:
            failures.append(f"prompt too short: {name}")
        if name not in {"practical_skills", "llm_judge"}:
            for phrase in REQUIRED_PHRASES:
                if phrase not in prompt.body:
                    failures.append(f"missing {phrase!r}: {name}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Validated {len(PROMPT_NAMES)} prompts")


if __name__ == "__main__":
    main()
