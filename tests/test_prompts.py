from __future__ import annotations

from four_pillars.prompts import PROMPT_NAMES, load_prompt, prompt_manifest


def test_all_prompts_have_versions_and_hashes() -> None:
    manifest = prompt_manifest()
    assert set(manifest) == set(PROMPT_NAMES)
    assert all(item["version"] == "1.0.0" for item in manifest.values())
    assert all(len(item["sha256"]) == 64 for item in manifest.values())


def test_monthly_prompt_requires_balanced_relationship_guidance() -> None:
    body = load_prompt("monthly_analysis").body
    assert "relationship section must not consist only of warnings" in body
    assert "calendar blocks" in body
    assert "24-hour cooling rule" in body


def test_prompts_preserve_deterministic_calculation_boundary() -> None:
    for name in ("natal_analysis", "daewoon_analysis", "annual_analysis", "monthly_analysis"):
        body = load_prompt(name).body
        assert "Never recalculate" in body or "Do not change" in body or "Preserve" in body
        assert "Output" in body
