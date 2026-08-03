from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from four_pillars.calendar import calculate_chart
from four_pillars.fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from four_pillars.models import BirthInput, Gender, PracticalSkill, ReportDocument, ReportSection
from four_pillars.reporting import render_html, render_pdf, write_artifacts


KEYS = ("natal", "daewoon", "annual", "monthly", "work", "money", "relationships", "daily_rhythm")


def report() -> ReportDocument:
    sections = {
        key: ReportSection(
            title=key,
            summary="혜지 님은 계산 근거와 현실 조건을 함께 확인합니다.",
            opportunities=["구체적인 합의를 통해 신뢰와 협력을 높일 수 있습니다."],
            cautions=["피로할 때 중요한 결정을 서두르지 않습니다."],
            actions=["담당 범위, 기한, 지원, 보상을 기록합니다."],
            examples=["회의 후 확인 메일을 보냅니다."],
            evidence=["월운 丙申"],
        )
        for key in KEYS
    }
    return ReportDocument(
        subject_name="<script>alert(1)</script>",
        title="테스트 사주 보고서",
        executive_summary="혜지 님은 현실적인 선택 기준을 세울 수 있습니다.",
        calculation_fingerprint="a" * 64,
        sections=sections,
        practical_skills=[
            PracticalSkill(
                name="주간 검토",
                purpose="캘린더의 확정 일정과 가안 일정을 구분합니다.",
                steps=["캘린더를 엽니다.", "완충 시간을 확보합니다."],
                when_to_use="매주 한 번 사용합니다.",
            )
        ],
        disclaimer="이 보고서는 전통 명리학의 상징 자료입니다. 의학·법률·재정 판단은 실제 정보와 전문가 의견을 우선합니다.",
        generated_at=datetime.now(UTC),
        model="test-model",
        prompt_versions={"synthesis": "1.0.0"},
    )


def bundle():
    chart = calculate_chart(BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul"))
    daewoon = calculate_daewoon(chart, Gender.FEMALE, count=2)
    annual = calculate_annual_luck(chart, 2026)
    monthly = calculate_monthly_luck(chart, 2026, 8)
    return chart, daewoon, annual, monthly


def test_html_escapes_user_controlled_text() -> None:
    chart, daewoon, annual, monthly = bundle()
    content = render_html(report(), chart, daewoon, annual, monthly)
    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in content
    assert "丙申" in content


def test_pdf_is_created_with_korean_report_content(tmp_path: Path) -> None:
    chart, daewoon, annual, monthly = bundle()
    target = tmp_path / "report.pdf"
    render_pdf(target, report(), chart, daewoon, annual, monthly)
    assert target.read_bytes().startswith(b"%PDF")
    assert target.stat().st_size > 2000


def test_artifact_manifest_hashes_every_output(tmp_path: Path) -> None:
    chart, daewoon, annual, monthly = bundle()
    output = tmp_path / "job"
    hashes = write_artifacts(
        output,
        report=report().model_copy(update={"calculation_fingerprint": chart.fingerprint}),
        chart=chart,
        daewoon=daewoon,
        annual=annual,
        monthly=monthly,
        traces={"synthesis": {"model": "test-model", "attempts": 1, "repairs": 0}},
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert (output / "report.pdf").is_file()
    assert (output / "report.html").is_file()
    assert manifest["calculation_fingerprint"] == chart.fingerprint
    assert hashes["report.pdf"] == manifest["files"]["report.pdf"]
