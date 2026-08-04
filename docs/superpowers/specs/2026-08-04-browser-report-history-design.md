# Browser Report History Design

## Goal

Complete the recoverability workflow introduced by the v0.5 report-history API by adding a responsive, accessible recent-job surface to the existing self-contained browser studio.

## Figma source

The editable product-design reference is **Four Pillars — Report History Studio**:

- File: https://www.figma.com/design/vkRt2HNNZjiAH4IGxeB8RX
- Desktop frame: `2:3`
- Mobile frame: `2:136`

The design extends the existing navy, blue, coral, teal, gold, off-white, and white visual system rather than introducing another application shell. On desktop, the current input and calculation panels remain side by side and a full-width history panel appears below them. On mobile, history collapses into one vertical panel with full-width actions.

## Product gap

The API can now enumerate durable recent jobs, but the browser still requires a user to retain an individual UUID in page memory. A refresh, tab close, API restart, or operational handoff therefore leaves the user-facing recovery flow incomplete even though the server safely retains the work.

## User workflow

1. The page loads the first 20 jobs from `GET /v1/reports`.
2. The user may filter by exact lifecycle status.
3. Refresh reloads the first page and announces the result through a dedicated polite live region.
4. “이전 작업 더 불러오기” follows `next_cursor` and appends the next page without replacing earlier rows.
5. Completed rows expose only server-supplied allow-listed artifact names as download links.
6. Queued or running rows expose “상태 보기”, restore that job into the existing current-job panel, and resume polling.
7. Failed and quality-failed rows display bounded public error text without rendering HTML.
8. A newly enqueued job refreshes history so it is immediately discoverable.
9. Changing the API key reloads history for the new authorization context.

## Information architecture

The history panel contains:

- numbered section heading “3 최근 보고서 작업”;
- privacy helper stating that names, birth input, and notes are not shown;
- status filter with all public `JobStatus` values;
- refresh control;
- dedicated `aria-live="polite"` history status;
- newest-first list;
- status chip with visible text, not color alone;
- shortened UUID, localized creation time, bounded status/error detail, and action area;
- hidden load-more control that appears only when `next_cursor` is present.

No subject name, birth date, user context, fingerprint, idempotency material, generated prose, trace content, or artifact path is requested or inferred by the browser.

## Interaction and accessibility

- Every control is a native button, select, or anchor.
- History updates use `replaceChildren`, `textContent`, and programmatically created nodes; no API-derived string is assigned through `innerHTML`.
- The active load state disables refresh, filter, and load-more controls to prevent duplicate requests.
- Status is communicated with Korean text and a semantic CSS class.
- Artifact anchors preserve the existing same-origin authenticated deployment assumption and use server-provided allow-listed filenames.
- Empty, unauthorized, unsupported-adapter, network-error, and end-of-history states have explicit Korean messages.
- Mobile layout preserves readable tap targets and avoids horizontal scrolling.
- Motion remains unnecessary; `prefers-reduced-motion` behavior is preserved.

## Error states

- HTTP 401: “API 키가 필요한 환경입니다. 키를 입력한 뒤 새로고침하세요.”
- HTTP 501: “현재 저장소는 최근 작업 조회를 지원하지 않습니다.”
- Empty page: “표시할 최근 작업이 없습니다.”
- Other errors: bounded API detail is shown as text in the history live region.
- Failed row: status and bounded error are visible; no generated report content is exposed.

## Architecture

The frontend remains a self-contained static HTML delivery adapter in `web.py`. It calls the existing versioned API and introduces no new backend state, database object, or MSA requirement. All durable ordering, filtering, cursor validation, privacy redaction, and adapter capability checks remain owned by the application and repository layers.

## Acceptance criteria

- Desktop and mobile markup follows the Figma information hierarchy and established visual tokens.
- First-page load, refresh, status filtering, cursor append, completed artifact links, active-job polling, and new-job refresh are wired.
- All API-derived text is inserted through safe DOM APIs.
- API keys remain only in current page memory.
- The panel never displays or reconstructs personal birth or report-request data.
- Existing calculation and report-generation workflows remain unchanged.
- Browser source tests, all offline tests, 100% statement/branch coverage, packaging, container, Security Scan, and Semgrep pass on the exact merge candidate.
