# KASI Solar-Term Golden Fixtures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add offline, authoritative 2026 KASI fixtures that verify every month-changing solar term and its buyer-visible year/month pillar transition.

**Architecture:** Commit a minute-precision external evidence file instead of adding a runtime ephemeris dependency or live CI lookup. Focused pytest cases validate fixture integrity, enforce a 120-second timing budget, and test chart transitions five minutes around each boundary; hourly product-gap governance prevents the evidence and doctoring from disappearing.

**Tech Stack:** Python 3.11/3.12, pytest, Pydantic models, deterministic calendar API, JSON fixtures, Markdown doctoring, GitHub Actions.

## Global Constraints

- The KASI fixture is immutable offline evidence, never runtime configuration.
- Exactly twelve month-changing `jie` terms for calendar year 2026 are required.
- Expected instants are timezone-aware ISO-8601 values in `Asia/Seoul` / UTC+09:00.
- Maximum absolute timing error is exactly 120 seconds.
- Month transitions are tested five minutes before and after each published instant.
- Li Chun additionally changes the year pillar from `乙巳` to `丙午`.
- No new production or test dependency is added.
- No network, model credential, or user data enters the test path.
- Standalone and modular MSA interfaces remain unchanged.
- Production statement and branch coverage remain exactly 100 percent.
- Public production APIs retain complete beginner-readable docstrings.
- APA 7 source provenance and claim boundaries are recorded in doctoring.
- The change remains under `Unreleased`; v0.8.0 is not rewritten.

---

### Task 1: Lock the missing authority-evidence contract

**Files:**
- Create: `tests/test_solar_term_golden.py`
- Existing design: `docs/superpowers/specs/2026-08-07-kasi-solar-term-golden-fixtures-design.md`

**Interfaces:**
- Consumes: repository paths only.
- Produces: a RED contract requiring the fixture and doctoring before astronomy assertions can run.

- [ ] **Step 1: Write the failing existence contract**

Create `tests/test_solar_term_golden.py`:

```python
"""Validate month-changing solar terms against authoritative KASI evidence."""

from __future__ import annotations

from pathlib import Path

FIXTURE = Path("tests/fixtures/kasi_2026_jie_terms.json")
DOCTORING = Path("docs/doctoring/kasi-solar-term-golden-fixtures.md")


def test_authoritative_solar_term_evidence_is_committed() -> None:
    """Require offline KASI data and its provenance before trusting boundaries."""

    assert FIXTURE.is_file()
    assert DOCTORING.is_file()
```

- [ ] **Step 2: Run the focused test and preserve RED evidence**

Run:

```bash
pytest tests/test_solar_term_golden.py -v
```

Expected: one failure because both required evidence files are absent.

- [ ] **Step 3: Commit the RED contract**

```bash
git add tests/test_solar_term_golden.py
git commit -m "test(calendar): require KASI solar-term evidence"
```

### Task 2: Add the immutable KASI fixture and timing tests

**Files:**
- Create: `tests/fixtures/kasi_2026_jie_terms.json`
- Modify: `tests/test_solar_term_golden.py`

**Interfaces:**
- Consumes: `four_pillars.calendar.jie_terms`, `four_pillars.calendar.calculate_chart`, `four_pillars.models.BirthInput`.
- Produces: parsed fixture records, timing delta assertions, month-transition assertions, and Li Chun year-transition evidence.

- [ ] **Step 1: Commit the exact external evidence data**

Create `tests/fixtures/kasi_2026_jie_terms.json`:

```json
{
  "schema_version": "1.0.0",
  "source_title": "2026년 달력자료(월력요항)",
  "source_url": "https://astro.kasi.re.kr/life/post/calendardata",
  "source_timezone": "Asia/Seoul",
  "published_precision": "minute",
  "retrieved_on": "2026-08-07",
  "maximum_absolute_error_seconds": 120,
  "terms": [
    {"name_ko": "소한", "longitude": 285.0, "expected_kst": "2026-01-05T17:23:00+09:00", "month_branch": "丑"},
    {"name_ko": "입춘", "longitude": 315.0, "expected_kst": "2026-02-04T05:02:00+09:00", "month_branch": "寅"},
    {"name_ko": "경칩", "longitude": 345.0, "expected_kst": "2026-03-05T22:59:00+09:00", "month_branch": "卯"},
    {"name_ko": "청명", "longitude": 15.0, "expected_kst": "2026-04-05T03:40:00+09:00", "month_branch": "辰"},
    {"name_ko": "입하", "longitude": 45.0, "expected_kst": "2026-05-05T20:49:00+09:00", "month_branch": "巳"},
    {"name_ko": "망종", "longitude": 75.0, "expected_kst": "2026-06-06T00:48:00+09:00", "month_branch": "午"},
    {"name_ko": "소서", "longitude": 105.0, "expected_kst": "2026-07-07T10:57:00+09:00", "month_branch": "未"},
    {"name_ko": "입추", "longitude": 135.0, "expected_kst": "2026-08-07T20:43:00+09:00", "month_branch": "申"},
    {"name_ko": "백로", "longitude": 165.0, "expected_kst": "2026-09-07T23:41:00+09:00", "month_branch": "酉"},
    {"name_ko": "한로", "longitude": 195.0, "expected_kst": "2026-10-08T15:29:00+09:00", "month_branch": "戌"},
    {"name_ko": "입동", "longitude": 225.0, "expected_kst": "2026-11-07T18:52:00+09:00", "month_branch": "亥"},
    {"name_ko": "대설", "longitude": 255.0, "expected_kst": "2026-12-07T11:53:00+09:00", "month_branch": "子"}
  ]
}
```

- [ ] **Step 2: Expand the test into a strict fixture loader**

Replace `tests/test_solar_term_golden.py` with focused helpers and contracts:

```python
"""Validate month-changing solar terms against authoritative KASI evidence."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from four_pillars.calendar import calculate_chart, jie_terms
from four_pillars.models import BirthInput

FIXTURE = Path("tests/fixtures/kasi_2026_jie_terms.json")
DOCTORING = Path("docs/doctoring/kasi-solar-term-golden-fixtures.md")
EXPECTED_NAMES = (
    "소한",
    "입춘",
    "경칩",
    "청명",
    "입하",
    "망종",
    "소서",
    "입추",
    "백로",
    "한로",
    "입동",
    "대설",
)


def _fixture() -> dict[str, Any]:
    """Return the committed external-evidence fixture as decoded JSON."""

    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _records() -> list[dict[str, Any]]:
    """Return ordered solar-term records from the committed fixture."""

    return list(_fixture()["terms"])


def test_authoritative_solar_term_evidence_is_committed() -> None:
    """Require offline KASI data and its provenance before trusting boundaries."""

    assert FIXTURE.is_file()
    assert DOCTORING.is_file()


def test_kasi_fixture_schema_and_scope_are_bounded() -> None:
    """Reject silent timezone, tolerance, order, or coverage changes."""

    fixture = _fixture()
    records = _records()

    assert fixture["schema_version"] == "1.0.0"
    assert fixture["source_timezone"] == "Asia/Seoul"
    assert fixture["published_precision"] == "minute"
    assert fixture["maximum_absolute_error_seconds"] == 120
    assert tuple(record["name_ko"] for record in records) == EXPECTED_NAMES
    assert len({record["name_ko"] for record in records}) == 12
    assert all(datetime.fromisoformat(record["expected_kst"]).utcoffset() == timedelta(hours=9) for record in records)


@pytest.mark.parametrize("record", _records(), ids=lambda record: record["name_ko"])
def test_calculated_jie_matches_kasi_within_two_minutes(record: dict[str, Any]) -> None:
    """Keep every calculated 2026 month boundary within the published budget."""

    calculated = {term.name_ko: term for term in jie_terms(2026, "Asia/Seoul")}
    expected = datetime.fromisoformat(record["expected_kst"])
    actual = calculated[record["name_ko"]].occurs_at
    delta_seconds = (actual - expected).total_seconds()

    assert calculated[record["name_ko"]].longitude == record["longitude"]
    assert abs(delta_seconds) <= _fixture()["maximum_absolute_error_seconds"], (
        f"{record['name_ko']} differs from KASI by {delta_seconds:+.3f} seconds"
    )


@pytest.mark.parametrize("record", _records(), ids=lambda record: record["name_ko"])
def test_published_jie_changes_month_branch_on_the_expected_side(record: dict[str, Any]) -> None:
    """Change each buyer-visible month pillar across the official boundary."""

    expected = datetime.fromisoformat(record["expected_kst"])
    before = calculate_chart(
        BirthInput(birth=(expected - timedelta(minutes=5)).replace(tzinfo=None), timezone="Asia/Seoul")
    )
    after = calculate_chart(
        BirthInput(birth=(expected + timedelta(minutes=5)).replace(tzinfo=None), timezone="Asia/Seoul")
    )

    assert before.month.branch != record["month_branch"]
    assert after.month.branch == record["month_branch"]


def test_kasi_lichun_changes_the_2026_year_pillar() -> None:
    """Change the sexagenary year across the independently published Li Chun."""

    record = next(record for record in _records() if record["name_ko"] == "입춘")
    expected = datetime.fromisoformat(record["expected_kst"])
    before = calculate_chart(
        BirthInput(birth=(expected - timedelta(minutes=5)).replace(tzinfo=None), timezone="Asia/Seoul")
    )
    after = calculate_chart(
        BirthInput(birth=(expected + timedelta(minutes=5)).replace(tzinfo=None), timezone="Asia/Seoul")
    )

    assert before.year.hanja == "乙巳"
    assert after.year.hanja == "丙午"
```

- [ ] **Step 3: Run fixture and timing tests**

Run:

```bash
pytest tests/test_solar_term_golden.py -v
```

Expected: the evidence-existence test still fails only because doctoring is absent; schema and astronomical assertions either pass or reveal signed timing deltas for root-cause analysis.

- [ ] **Step 4: Diagnose any timing failure before changing production code**

For every failed term, record the signed delta. Treat nearly constant deltas as timezone/timescale issues, smooth seasonal drift as model error, and an isolated outlier as transcription risk. Re-check the KASI source before editing `src/four_pillars/calendar.py`.

If every absolute delta is at most 120 seconds, do not change production calculation code.

- [ ] **Step 5: Commit the immutable data and focused tests**

```bash
git add tests/fixtures/kasi_2026_jie_terms.json tests/test_solar_term_golden.py
git commit -m "test(calendar): add KASI 2026 solar-term fixtures"
```

### Task 3: Add provenance, APA 7 traceability, and hourly regression detection

**Files:**
- Create: `docs/doctoring/kasi-solar-term-golden-fixtures.md`
- Modify: `docs/technical/CALCULATION.md`
- Modify: `docs/standards/REFERENCES.md`
- Modify: `docs/standards/TRACEABILITY.md`
- Modify: `scripts/product_gap_audit.py`
- Modify: `tests/test_hourly_product_loop.py`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: fixture path and exact source tokens.
- Produces: `AUTHORITY_FIXTURE_CONTRACTS` and `audit_authority_fixture_contract(root: Path) -> list[ProductGap]`.

- [ ] **Step 1: Write the doctoring source and claim boundary**

Create `docs/doctoring/kasi-solar-term-golden-fixtures.md` with these sections:

```markdown
# KASI 2026 Solar-Term Golden Fixtures — Evidence Doctoring

## Buyer-visible claim
## Source selection
## Transcription and timezone policy
## Accuracy budget
## Boundary test design
## Claim boundary and residual risk
## Research-tool limitations
## APA 7th references
```

The document must state that KASI publishes Korean Standard Time to minute precision, the fixture is transcribed rather than fetched during CI, the 120-second limit allows source rounding, NAOJ independently agrees for July 2026, DE440 is context rather than the direct fixture generator, and Consensus search quota was exhausted.

Include these APA 7 references:

```markdown
Korea Astronomy and Space Science Institute. (n.d.). *달력자료(월력요항): 2026년 달력자료*. Retrieved August 7, 2026, from https://astro.kasi.re.kr/life/post/calendardata

Korea Astronomy and Space Science Institute. (2025, June 30). *「2026년 월력요항」 발표*. https://www.kasi.re.kr/kor/publication/post/newsMaterial/32031

National Astronomical Observatory of Japan. (n.d.). *Monthly calendar*. Retrieved August 7, 2026, from https://eco2.mtk.nao.ac.jp/cgi-bin/koyomi/monthly_en.cgi

Park, R. S., Folkner, W. M., Williams, J. G., & Boggs, D. H. (2021). The JPL planetary and lunar ephemerides DE440 and DE441. *The Astronomical Journal, 161*(3), 105. https://doi.org/10.3847/1538-3881/abd414
```

- [ ] **Step 2: Extend calculation and standards documentation**

In `docs/technical/CALCULATION.md`, add a `## Independent boundary validation` section that names `tests/fixtures/kasi_2026_jie_terms.json`, KASI 2026, the 120-second budget, five-minute transition tests, and the fact that official minute precision does not imply research-grade certification.

Append the KASI, NAOJ, and Park et al. references to `docs/standards/REFERENCES.md` in APA 7th form. In `docs/standards/TRACEABILITY.md`, map the official fixture to functional correctness, `tests/test_solar_term_golden.py`, the hourly audit, and the residual risk from historical timezones and analytical approximations.

- [ ] **Step 3: Add the authority-fixture audit contract**

In `scripts/product_gap_audit.py`, add:

```python
AUTHORITY_FIXTURE_CONTRACTS = (
    (
        "tests/fixtures/kasi_2026_jie_terms.json",
        '"maximum_absolute_error_seconds": 120',
    ),
    (
        "docs/doctoring/kasi-solar-term-golden-fixtures.md",
        "Korea Astronomy and Space Science Institute",
    ),
    ("docs/technical/CALCULATION.md", "KASI 2026"),
    ("docs/standards/REFERENCES.md", "10.3847/1538-3881/abd414"),
    ("docs/standards/TRACEABILITY.md", "kasi_2026_jie_terms.json"),
)
```

Add:

```python
def audit_authority_fixture_contract(root: Path) -> list[ProductGap]:
    """Return gaps in independent solar-term evidence and provenance."""

    return _audit_token_contracts(
        root,
        AUTHORITY_FIXTURE_CONTRACTS,
        code="authority_fixture_contract",
        label="Authority fixture contract",
    )
```

Call `gaps.extend(audit_authority_fixture_contract(root))` from `audit_repository` after the standards contract.

- [ ] **Step 4: Test deletion and token drift detection**

In `tests/test_hourly_product_loop.py`, add:

```python
def test_authority_fixture_contract_audit_detects_missing_tokens(tmp_path: Path) -> None:
    """Keep official solar-term evidence and provenance inside the hourly gate."""

    module = load_audit_module()
    assert_token_contract_detects_missing_entries(
        tmp_path,
        module.AUTHORITY_FIXTURE_CONTRACTS,
        "audit_authority_fixture_contract",
    )
```

Extend `test_standards_doctoring_contains_authoritative_and_peer_reviewed_sources` to require `Korea Astronomy and Space Science Institute`, `National Astronomical Observatory of Japan`, and `10.3847/1538-3881/abd414`.

- [ ] **Step 5: Record the unreleased buyer-visible validation**

Under `CHANGELOG.md` → `Unreleased`, add:

```markdown
### Added

- Independent KASI 2026 golden fixtures for all twelve month-changing solar terms, enforcing a two-minute timing budget and five-minute year/month pillar transition checks without network or test-only ephemeris dependencies.

### Changed

- Calculation and standards doctoring now trace official Korean calendar evidence, NAOJ cross-check context, JPL DE440 claim boundaries, and hourly regression detection for fixture or provenance drift.
```

Remove the completed “Additional independent golden-chart fixtures near solar-term boundaries” item from `Unreleased` → `Planned`.

- [ ] **Step 6: Run focused documentation and audit tests**

Run:

```bash
python scripts/check_docs.py
pytest tests/test_solar_term_golden.py tests/test_hourly_product_loop.py -v
python scripts/product_gap_audit.py
```

Expected: all commands pass; the solar-term timing budget remains at 120 seconds and the repository audit reports zero gaps.

- [ ] **Step 7: Commit provenance and governance**

```bash
git add CHANGELOG.md docs/doctoring/kasi-solar-term-golden-fixtures.md docs/technical/CALCULATION.md docs/standards/REFERENCES.md docs/standards/TRACEABILITY.md scripts/product_gap_audit.py tests/test_hourly_product_loop.py
git commit -m "docs(calendar): trace KASI boundary evidence"
```

### Task 4: Complete exact-head verification, review, and merge

**Files:**
- Verify: every changed fixture, test, script, and document.

**Interfaces:**
- Produces: one reviewed PR with no release, deployment, or runtime credential changes.

- [ ] **Step 1: Run the full release-quality gate**

Run:

```bash
python -m pip check
python scripts/product_gap_audit.py
ruff check .
python -m compileall -q src tests scripts
python scripts/check_docs.py
python scripts/check_prompts.py
pytest -m 'not nim_live' -W error::ResourceWarning --cov=four_pillars --cov-report=term-missing
python -m build --no-isolation
docker build --tag four-pillars:kasi-golden .
```

Expected: every command succeeds with exactly 100 percent production statement and branch coverage.

- [ ] **Step 2: Review current-head changes and all Checks**

Inspect the complete diff, comments, review submissions, inline threads, Python 3.11/3.12 jobs, container, Security Scan, Semgrep, and every current-head check run. Correct every actionable finding before merge.

- [ ] **Step 3: Confirm no unintended behavior or dependency change**

Verify that `pyproject.toml`, `src/four_pillars/calendar.py`, API schemas, prompts, database schema, worker, and model adapters are unchanged unless signed timing-delta evidence required a narrowly reviewed calculation fix.

- [ ] **Step 4: Merge with expected-head protection**

Squash merge only after all current-head checks succeed and unresolved actionable review threads are zero.

- [ ] **Step 5: Re-enter the autonomous loop**

Confirm open PRs and issues are zero, verify main-branch checks, and select the next bounded buyer-visible gap. Consider a patch release only after evaluating all accumulated post-v0.8.0 changes.