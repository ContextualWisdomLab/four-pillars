from __future__ import annotations

from four_pillars.web import render_home


def test_browser_workflow_contains_calculation_review_and_report_polling() -> None:
    page = render_home()
    assert 'id="report-form"' in page
    assert 'id="calculate"' in page
    assert 'id="generate" disabled' in page
    assert "'/v1/chart'" in page
    assert "'/v1/reports'" in page
    assert "job.artifacts.forEach" in page
    assert "/artifacts/${name}" in page
    assert "계산 fingerprint" in page
    assert "경계" in page


def test_browser_workflow_exposes_privacy_safe_recent_report_recovery() -> None:
    page = render_home()

    for element_id in (
        "history",
        "history-filter",
        "history-refresh",
        "history-status",
        "history-list",
        "history-more",
    ):
        assert f'id="{element_id}"' in page
    assert 'id="history-status" role="status" aria-live="polite"' in page
    assert "이름·생년월일·상황 메모는 표시하지 않습니다" in page
    for status in (
        "queued",
        "running",
        "completed",
        "failed",
        "quality_failed",
    ):
        assert f'<option value="{status}">' in page


def test_browser_history_loads_filters_appends_and_restores_active_jobs() -> None:
    page = render_home()

    for contract in (
        "async function loadHistory",
        "new URLSearchParams",
        "payload.next_cursor",
        "historyFilter.addEventListener('change'",
        "historyRefresh.addEventListener('click'",
        "historyMore.addEventListener('click'",
        "loadHistory({reset:true})",
        "poll(job.id)",
        "/artifacts/${name}",
    ):
        assert contract in page
    assert "historyCursor" in page
    assert "historyLoading" in page
    assert "renderHistoryItem" in page
    assert "historyList.appendChild" in page


def test_browser_history_discards_stale_requests_and_respects_reduced_motion() -> None:
    page = render_home()

    assert "historyRequest" in page
    assert "const requestId=++historyRequest" in page
    assert "requestId!==historyRequest" in page
    assert "if(requestId===historyRequest)setHistoryLoading(false)" in page
    assert "matchMedia('(prefers-reduced-motion: reduce)')" in page
    assert "behavior:reduced?'auto':'smooth'" in page


def test_browser_polling_discards_stale_jobs_and_clears_auth_context() -> None:
    page = render_home()

    assert "pollRequest" in page
    assert "const requestId=++pollRequest" in page
    assert "requestId!==pollRequest" in page
    assert "function clearCurrentJob" in page
    assert "pollRequest+=1" in page
    assert "apiKey.addEventListener('change',()=>{clearCurrentJob();loadHistory({reset:true})})" in page
    assert "message('입력을 초기화했습니다.');clearCurrentJob();loadHistory({reset:true})" in page


def test_browser_history_uses_authenticated_downloads_and_bounded_error_copy() -> None:
    page = render_home()

    assert "async function downloadArtifact" in page
    assert "fetch(`/v1/reports/${jobId}/artifacts/${name}`,{headers:headers()})" in page
    assert "URL.createObjectURL" in page
    assert "link.download=name" in page
    assert "setTimeout(()=>URL.revokeObjectURL(url),1000)" in page
    assert "function boundedHistoryDetail" in page
    assert "slice(0,239)" in page
    assert "historyMessage(boundedHistoryDetail(text),true)" in page
    assert "message(boundedHistoryDetail(error.message),true)" in page


def test_browser_history_uses_safe_dom_and_ephemeral_state_only() -> None:
    page = render_home()

    assert "replaceChildren" in page
    assert "textContent" in page
    assert "document.createElement" in page
    assert "innerHTML" not in page
    assert "localStorage" not in page
    assert "sessionStorage" not in page
    assert "indexedDB" not in page
    assert "document.cookie" not in page


def test_browser_workflow_does_not_persist_api_key() -> None:
    page = render_home()
    assert 'id="api-key" type="password"' in page
    assert "localStorage" not in page
    assert "sessionStorage" not in page
    assert "X-API-Key" in page
    assert "apiKey.addEventListener('change'" in page


def test_browser_workflow_is_responsive_and_accessibility_aware() -> None:
    page = render_home()
    assert 'aria-live="polite"' in page
    assert "prefers-reduced-motion" in page
    assert "@media(max-width:850px)" in page
    assert ".history-panel{grid-column:1/-1}" in page
    assert ".history-item" in page
    assert ".history-chip" in page
    assert "생년월일시와 상황 메모는 민감정보" in page
