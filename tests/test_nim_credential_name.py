from __future__ import annotations


CANONICAL_ENV_NAME = "NVIDIA_NIM_API_KEY"
LEGACY_ENV_NAME = "NVIDIA_" + "API_KEY"


def test_settings_reads_the_canonical_nim_credential(monkeypatch) -> None:
    from four_pillars.settings import Settings

    monkeypatch.delenv(LEGACY_ENV_NAME, raising=False)
    monkeypatch.setenv(CANONICAL_ENV_NAME, "nim-secret")

    settings = Settings(_env_file=None)

    assert settings.nvidia_nim_api_key == "nim-secret"


def test_legacy_credential_name_is_not_silently_accepted(monkeypatch) -> None:
    from four_pillars.settings import Settings

    monkeypatch.delenv(CANONICAL_ENV_NAME, raising=False)
    monkeypatch.setenv(LEGACY_ENV_NAME, "legacy-secret")

    settings = Settings(_env_file=None)

    assert settings.nvidia_nim_api_key is None


def test_repository_uses_only_the_canonical_nim_credential_name() -> None:
    from pathlib import Path

    text_suffixes = {".md", ".py", ".toml", ".yaml", ".yml"}
    ignored_parts = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "build",
        "dist",
    }
    offenders: list[str] = []

    for path in Path(".").rglob("*"):
        if not path.is_file() or ignored_parts.intersection(path.parts):
            continue
        if path.name != ".env.example" and path.suffix not in text_suffixes:
            continue
        if path == Path(__file__):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if LEGACY_ENV_NAME in text:
            offenders.append(path.as_posix())

    assert not offenders, f"Replace {LEGACY_ENV_NAME} with {CANONICAL_ENV_NAME}: {offenders}"
