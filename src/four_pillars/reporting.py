"""Render approved reports and atomically publish integrity-hashed artifacts."""

from __future__ import annotations

import hashlib
import html
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .models import Chart, DaewoonResult, LuckSnapshot, ReportDocument, ReportSection

NAVY = colors.HexColor("#17263F")
BLUE = colors.HexColor("#315A84")
CORAL = colors.HexColor("#D16F58")
TEAL = colors.HexColor("#4F8F8A")
GOLD = colors.HexColor("#C5A165")
PAGE = colors.HexColor("#FBFAF6")
MUTED = colors.HexColor("#667283")
BORDER = colors.HexColor("#D9D7CF")


def _safe(value: object) -> str:
    return html.escape(str(value), quote=True).replace("\n", "<br/>")


def _section_html(section: ReportSection) -> str:
    def items(values: list[str]) -> str:
        return "".join(f"<li>{_safe(value)}</li>" for value in values)

    return f"""
<section class="report-section">
  <h2>{_safe(section.title)}</h2>
  <p class="summary">{_safe(section.summary)}</p>
  <div class="columns">
    <article class="card opportunity"><h3>긍정적 가능성</h3><ul>{items(section.opportunities)}</ul></article>
    <article class="card caution"><h3>주의할 점</h3><ul>{items(section.cautions)}</ul></article>
  </div>
  <article class="actions"><h3>실천 방법</h3><ol>{items(section.actions)}</ol></article>
</section>
"""


def render_html(
    report: ReportDocument,
    chart: Chart,
    daewoon: DaewoonResult,
    annual: LuckSnapshot,
    monthly: LuckSnapshot,
) -> str:
    """Render a self-contained, escaped, responsive Korean HTML report."""
    hour = chart.hour.hanja if chart.hour is not None else "미확정"
    sections = "".join(_section_html(section) for section in report.sections.values())
    skills = "".join(
        f"<article class='skill'><h3>{_safe(skill.name)}</h3><p>{_safe(skill.purpose)}</p>"
        f"<ol>{''.join(f'<li>{_safe(step)}</li>' for step in skill.steps)}</ol>"
        f"<p class='when'>{_safe(skill.when_to_use)}</p></article>"
        for skill in report.practical_skills
    )
    daewoon_rows = "".join(
        f"<tr><td>{scenario.label}</td><td>{scenario.start_age:.2f}세</td>"
        f"<td>{', '.join(period.pillar.hanja for period in scenario.periods[:4])}</td></tr>"
        for scenario in daewoon.scenarios
    )
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{_safe(report.title)}</title>
<style>
@page {{ size: A4; margin: 18mm 17mm; }}
:root {{ --navy:#17263f; --blue:#315a84; --coral:#d16f58; --teal:#4f8f8a; --gold:#c5a165; --page:#fbfaf6; --muted:#667283; }}
* {{ box-sizing:border-box; }} body {{ margin:0; color:var(--navy); background:var(--page); font-family:"Noto Sans KR","Apple SD Gothic Neo",sans-serif; line-height:1.65; }}
main {{ max-width:900px; margin:auto; padding:42px; }} header {{ background:var(--navy); color:white; padding:50px; border-radius:18px; }}
h1 {{ font-size:34px; margin:0 0 12px; }} h2 {{ margin-top:34px; border-left:6px solid var(--coral); padding-left:14px; }} h3 {{ margin-top:0; }}
.subject {{ font-size:14px; opacity:.82; }} .fingerprint {{ overflow-wrap:anywhere; opacity:.7; font-size:12px; }} .summary {{ font-size:17px; }} .columns {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.card,.actions,.skill {{ padding:20px; border-radius:10px; background:white; border:1px solid #e4e1d8; break-inside:avoid; }} .opportunity {{ border-top:5px solid var(--teal); }} .caution {{ border-top:5px solid var(--coral); }}
table {{ width:100%; border-collapse:collapse; margin:22px 0; background:white; }} th,td {{ padding:10px; border:1px solid #ddd9cf; text-align:left; }} th {{ background:#eaf1f7; }}
.when {{ color:var(--muted); }} .disclaimer {{ margin-top:40px; padding:20px; background:#f2efe8; border-left:5px solid var(--gold); }}
@media(max-width:700px) {{ main {{ padding:18px; }} .columns {{ grid-template-columns:1fr; }} }}
</style></head><body><main>
<header><p>FOUR PILLARS REPORT</p><h1>{_safe(report.title)}</h1><p class="subject">대상: {_safe(report.subject_name)}</p><p>{_safe(report.executive_summary)}</p><p class="fingerprint">계산 fingerprint: {_safe(report.calculation_fingerprint)}</p></header>
<section><h2>계산 요약</h2><table><tr><th>연주</th><th>월주</th><th>일주</th><th>시주</th></tr><tr><td>{chart.year.hanja}</td><td>{chart.month.hanja}</td><td>{chart.day.hanja}</td><td>{hour}</td></tr></table>
<table><tr><th>구분</th><th>시작</th><th>종료</th><th>간지</th></tr><tr><td>세운</td><td>{annual.starts_at:%Y-%m-%d}</td><td>{annual.ends_at:%Y-%m-%d}</td><td>{annual.pillar.hanja}</td></tr><tr><td>월운</td><td>{monthly.starts_at:%Y-%m-%d}</td><td>{monthly.ends_at:%Y-%m-%d}</td><td>{monthly.pillar.hanja}</td></tr></table>
<table><tr><th>대운 방향</th><th>시작 나이</th><th>초기 네 대운</th></tr>{daewoon_rows}</table></section>
{sections}
<section><h2>실용 기술</h2>{skills}</section>
<p class="disclaimer">{_safe(report.disclaimer)}</p>
</main></body></html>"""


def _register_fonts() -> tuple[str, str]:
    # ReportLab ships this Korean CID font without requiring a host font file.
    # Newer ReportLab releases no longer recognize HYGoThic-Medium, so the
    # portable CID face is used for both regular and emphasized styles.
    regular = "HYSMyeongJo-Medium"
    if regular not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(UnicodeCIDFont(regular))
    return regular, regular


def render_pdf(
    destination: Path,
    report: ReportDocument,
    chart: Chart,
    daewoon: DaewoonResult,
    annual: LuckSnapshot,
    monthly: LuckSnapshot,
) -> None:
    """Write a searchable A4 Korean PDF report with embedded document metadata."""
    regular, bold = _register_fonts()
    styles = getSampleStyleSheet()
    title = ParagraphStyle("KTitle", parent=styles["Title"], fontName=bold, fontSize=24, leading=32, textColor=NAVY, alignment=TA_LEFT, spaceAfter=16)
    heading = ParagraphStyle("KHeading", parent=styles["Heading2"], fontName=bold, fontSize=15, leading=21, textColor=NAVY, borderColor=CORAL, borderWidth=0, leftIndent=0, spaceBefore=14, spaceAfter=8)
    subheading = ParagraphStyle("KSub", parent=styles["Heading3"], fontName=bold, fontSize=10, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("KBody", parent=styles["BodyText"], fontName=regular, fontSize=8.5, leading=13.5, textColor=NAVY, spaceAfter=6)
    small = ParagraphStyle("KSmall", parent=body, fontSize=7, leading=11, textColor=MUTED)
    doc = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=report.title,
        author="Contextual Wisdom Lab",
        subject="Traditional Four Pillars reflection report",
    )
    story: list[Any] = [
        Paragraph("FOUR PILLARS REPORT", small),
        Paragraph(_safe(report.title), title),
        Paragraph(f"대상: {_safe(report.subject_name)}", small),
        Paragraph(_safe(report.executive_summary), body),
        Spacer(1, 8 * mm),
        Paragraph("계산 요약", heading),
    ]
    hour = chart.hour.hanja if chart.hour is not None else "미확정"
    table_data = [
        [Paragraph("연주", small), Paragraph("월주", small), Paragraph("일주", small), Paragraph("시주", small)],
        [Paragraph(chart.year.hanja, body), Paragraph(chart.month.hanja, body), Paragraph(chart.day.hanja, body), Paragraph(hour, body)],
    ]
    table = Table(table_data, colWidths=[42 * mm] * 4)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.5, BORDER), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story.extend([table, Paragraph(f"계산 fingerprint: {_safe(report.calculation_fingerprint)}", small), PageBreak()])

    for section in report.sections.values():
        story.append(Paragraph(_safe(section.title), heading))
        story.append(Paragraph(_safe(section.summary), body))
        for label, values, color in (("긍정적 가능성", section.opportunities, TEAL), ("주의할 점", section.cautions, CORAL), ("실천 방법", section.actions, BLUE)):
            story.append(Paragraph(label, subheading))
            for item in values:
                item_style = ParagraphStyle(f"item-{label}", parent=body, leftIndent=9, bulletIndent=0, textColor=NAVY, borderColor=color)
                story.append(Paragraph(_safe(item), item_style, bulletText="•"))
        story.append(Spacer(1, 4 * mm))

    story.append(PageBreak())
    story.append(Paragraph("실용 기술", heading))
    for skill in report.practical_skills:
        story.append(Paragraph(_safe(skill.name), subheading))
        story.append(Paragraph(_safe(skill.purpose), body))
        for step in skill.steps:
            story.append(Paragraph(_safe(step), body, bulletText="•"))
        story.append(Paragraph(f"사용 시점: {_safe(skill.when_to_use)}", small))
    story.extend([Spacer(1, 8 * mm), Paragraph("해석 범위와 유의사항", heading), Paragraph(_safe(report.disclaimer), body)])
    doc.build(story)


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_artifacts(
    directory: Path,
    *,
    report: ReportDocument,
    chart: Chart,
    daewoon: DaewoonResult,
    annual: LuckSnapshot,
    monthly: LuckSnapshot,
    traces: dict[str, dict[str, Any]],
) -> dict[str, str]:
    """Publish JSON, HTML, PDF, traces, and a SHA-256 manifest into a new directory."""
    directory.mkdir(parents=True, exist_ok=False)
    payloads = {
        "chart.json": chart.model_dump_json(indent=2).encode(),
        "daewoon.json": daewoon.model_dump_json(indent=2).encode(),
        "annual.json": annual.model_dump_json(indent=2).encode(),
        "monthly.json": monthly.model_dump_json(indent=2).encode(),
        "report.json": report.model_dump_json(indent=2).encode(),
        "traces.json": json.dumps(traces, ensure_ascii=False, indent=2).encode(),
    }
    for filename, data in payloads.items():
        _atomic_write(directory / filename, data)
    _atomic_write(
        directory / "report.html",
        render_html(report, chart, daewoon, annual, monthly).encode(),
    )
    render_pdf(directory / "report.pdf", report, chart, daewoon, annual, monthly)
    files = sorted(path for path in directory.iterdir() if path.is_file())
    hashes = {path.name: _digest(path) for path in files}
    manifest = {
        "calculation_fingerprint": chart.fingerprint,
        "model": report.model,
        "prompt_versions": report.prompt_versions,
        "files": hashes,
    }
    _atomic_write(
        directory / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2).encode(),
    )
    hashes["manifest.json"] = _digest(directory / "manifest.json")
    return hashes
