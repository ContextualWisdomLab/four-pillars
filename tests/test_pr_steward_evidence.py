"""Exercise the trusted pull-request steward evidence boundary."""

from __future__ import annotations

import importlib.util
import json
import stat
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path("scripts/prepare_pr_steward_evidence.py")


def load_script() -> ModuleType:
    """Load the evidence serializer as a directly testable module."""
    spec = importlib.util.spec_from_file_location("prepare_pr_steward_evidence", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def realistic_evidence() -> dict:
    """Return one realistic bounded exact-head review and Check document."""
    return {
        "schema_version": 1,
        "repository": "ContextualWisdomLab/four-pillars",
        "pull_request": {
            "number": 42,
            "title": "fix: 절기 경계 보고서 검증",
            "body": "실제 서울 시간대의 입춘 경계 회귀를 보강합니다.\r\n",
            "head_ref": "fix/solar-term-boundary",
            "head_sha": "a" * 40,
            "base_ref": "main",
            "base_sha": "b" * 40,
            "updated_at": "2026-08-07T10:00:00Z",
        },
        "review_decision": "CHANGES_REQUESTED",
        "reviews": [
            {
                "author": "review-agent[bot]",
                "state": "CHANGES_REQUESTED",
                "body": "한국 표준시 기준 경계 바로 전후 fixture를 추가해 주세요.",
            }
        ],
        "threads": [
            {
                "author": "review-agent[bot]",
                "path": "tests/test_calendar.py",
                "line": 88,
                "body": "경계 1초 전과 1초 후를 모두 검증해야 합니다.",
                "is_resolved": False,
            }
        ],
        "checks": [
            {
                "name": "quality (3.12)",
                "status": "completed",
                "conclusion": "failure",
                "details_url": "https://github.com/ContextualWisdomLab/four-pillars/actions/runs/123",
                "summary": "1 failed, 225 passed; expected month pillar differs at the boundary.",
            }
        ],
    }


def write_source(tmp_path: Path, value: object) -> Path:
    """Write one JSON source fixture and return its path."""
    source = tmp_path / "evidence.json"
    source.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return source


def test_prepare_evidence_normalizes_unicode_and_writes_private_canonical_json(tmp_path: Path) -> None:
    module = load_script()
    source_value = realistic_evidence()
    source_value["pull_request"]["title"] = "fix: Cafe\u0301 경계\r\n"
    source = write_source(tmp_path, source_value)
    output = tmp_path / "trusted" / "evidence.json"

    validated = module.prepare_evidence(source, output)

    assert validated["pull_request"]["title"] == "fix: Café 경계\n"
    assert validated["pull_request"]["body"].endswith("\n")
    assert stat.S_IMODE(output.stat().st_mode) == 0o600
    raw = output.read_text(encoding="utf-8")
    assert raw.endswith("\n")
    assert raw == json.dumps(
        validated,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def test_prepare_evidence_replaces_a_stale_private_temporary_file(tmp_path: Path) -> None:
    module = load_script()
    source = write_source(tmp_path, realistic_evidence())
    output = tmp_path / "trusted.json"
    temporary = tmp_path / ".trusted.json.tmp"
    temporary.write_text("stale", encoding="utf-8")

    module.prepare_evidence(source, output)

    assert output.is_file()
    assert not temporary.exists()


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda value: value.update(extra=True), "keys are invalid"),
        (lambda value: value.pop("checks"), "keys are invalid"),
        (lambda value: value.update(schema_version=2), "schema_version"),
        (lambda value: value.update(repository="owner"), "repository"),
        (lambda value: value.update(review_decision="UNKNOWN"), "review_decision"),
        (lambda value: value["pull_request"].update(number=True), "positive integer"),
        (lambda value: value["pull_request"].update(head_sha="ABC"), "head_sha"),
        (lambda value: value["pull_request"].update(head_ref="bad ref"), "head_ref"),
        (lambda value: value["reviews"][0].update(state="PENDING"), "state is invalid"),
        (lambda value: value["threads"][0].update(is_resolved="no"), "boolean"),
        (lambda value: value["threads"][0].update(line=0), "positive integer"),
        (lambda value: value["checks"][0].update(status="waiting"), "status is invalid"),
        (lambda value: value["checks"][0].update(conclusion="unknown"), "conclusion is invalid"),
        (
            lambda value: value["checks"][0].update(details_url="http://github.com/run"),
            "HTTPS GitHub URL",
        ),
        (
            lambda value: value["checks"][0].update(details_url="https://user@github.com/run"),
            "HTTPS GitHub URL",
        ),
        (
            lambda value: value["checks"][0].update(details_url="https://github.com/run#fragment"),
            "HTTPS GitHub URL",
        ),
        (lambda value: value["reviews"][0].update(body="line\u202e"), "bidirectional"),
        (lambda value: value["threads"][0].update(body="line\x00"), "control"),
        (lambda value: value["pull_request"].update(body="가" * 7_000), "byte budget"),
        (lambda value: value.update(reviews=[{}] * 101), "too many"),
        (lambda value: value.update(reviews="not-a-list"), "must be a list"),
    ],
)
def test_validate_evidence_rejects_malformed_or_unbounded_values(mutator, message: str) -> None:
    module = load_script()
    value = realistic_evidence()
    mutator(value)

    with pytest.raises(ValueError, match=message):
        module.validate_evidence(value)


def test_validate_evidence_accepts_empty_optional_url_line_and_decision() -> None:
    module = load_script()
    value = realistic_evidence()
    value["review_decision"] = ""
    value["threads"][0]["line"] = None
    value["checks"][0]["details_url"] = ""
    value["checks"][0]["conclusion"] = ""
    value["checks"][0]["status"] = "queued"

    validated = module.validate_evidence(value)

    assert validated["review_decision"] == ""
    assert validated["threads"][0]["line"] is None
    assert validated["checks"][0]["details_url"] == ""


def test_validate_evidence_rejects_non_objects_and_non_string_keys() -> None:
    module = load_script()
    with pytest.raises(ValueError, match="must be an object"):
        module.validate_evidence([])
    with pytest.raises(ValueError, match="keys must be strings"):
        module.validate_evidence({1: "bad"})


def test_prepare_evidence_rejects_encoding_json_size_and_non_regular_sources(tmp_path: Path) -> None:
    module = load_script()
    output = tmp_path / "out.json"

    invalid_utf8 = tmp_path / "invalid.json"
    invalid_utf8.write_bytes(bytes((255, 254)))
    with pytest.raises(ValueError, match="UTF-8"):
        module.prepare_evidence(invalid_utf8, output)

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="valid JSON"):
        module.prepare_evidence(malformed, output)

    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b"x" * 128_001)
    with pytest.raises(ValueError, match="byte budget"):
        module.prepare_evidence(oversized, output)

    with pytest.raises(ValueError, match="regular file"):
        module.prepare_evidence(tmp_path, output)

    target = write_source(tmp_path, realistic_evidence())
    link = tmp_path / "evidence-link.json"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks are unavailable on this platform")
    with pytest.raises(ValueError, match="regular file"):
        module.prepare_evidence(link, output)


def test_read_regular_file_reports_missing_and_open_failures(tmp_path: Path, monkeypatch) -> None:
    module = load_script()
    missing = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="readable regular file"):
        module._read_regular_file(missing)

    source = write_source(tmp_path, realistic_evidence())

    def fail_open(*_args, **_kwargs):
        raise OSError("denied")

    monkeypatch.setattr(module.os, "open", fail_open)
    with pytest.raises(ValueError, match="readable regular file"):
        module._read_regular_file(source)


def test_cli_returns_stable_success_and_validation_statuses(tmp_path: Path, capsys) -> None:
    module = load_script()
    source = write_source(tmp_path, realistic_evidence())
    output = tmp_path / "out.json"

    assert module.main([str(source), str(output)]) == 0
    bad = tmp_path / "bad.json"
    bad.write_text("[]", encoding="utf-8")
    assert module.main([str(bad), str(output)]) == 2
    assert "evidence validation failed" in capsys.readouterr().err
