from __future__ import annotations

from four_pillars.web import render_home


def test_browser_workflow_contains_calculation_review_and_report_polling() -> None:
    page = render_home()
    assert 'id="report-form"' in page
    assert 'id="calculate"' in page
    assert 'id="generate" disabled' in page
    assert "'/v1/chart'" in page
    assert "'/v1/reports'" in page
    assert "report.pdf" in page
    assert "계산 fingerprint" in page
    assert "경계" in page


def test_browser_workflow_does_not_persist_api_key() -> None:
    page = render_home()
    assert 'id="api-key" type="password"' in page
    assert "localStorage" not in page
    assert "sessionStorage" not in page
    assert "X-API-Key" in page


def test_browser_workflow_is_responsive_and_accessibility_aware() -> None:
    page = render_home()
    assert 'aria-live="polite"' in page
    assert "prefers-reduced-motion" in page
    assert "@media(max-width:850px)" in page
    assert "생년월일시와 상황 메모는 민감정보" in page
