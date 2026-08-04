# Browser Report History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a responsive, accessible recent-report workflow to the self-contained browser studio using the privacy-safe v0.5 history API.

**Architecture:** Keep the browser as one static HTML delivery adapter in `web.py`. The page owns only ephemeral filter, cursor, loading, and current-job state; durable ordering, privacy redaction, cursor validation, and repository capability checks remain behind `GET /v1/reports`. Build the visible hierarchy from the approved Figma frames without introducing a new frontend framework or persistent browser storage.

**Tech Stack:** Semantic HTML, CSS custom properties, native JavaScript DOM APIs and Fetch, FastAPI endpoints, pytest source-contract tests, GitHub Actions.

## Global Constraints

- Follow Figma file `vkRt2HNNZjiAH4IGxeB8RX`, desktop frame `2:3`, and mobile frame `2:136`.
- Do not use `localStorage`, `sessionStorage`, cookies, IndexedDB, or URL parameters for the API key or job data.
- Do not use `innerHTML` for API-derived values.
- Do not request or infer subject names, birth data, user context, fingerprints, idempotency material, generated report copy, traces, or artifact paths.
- `NVIDIA_NIM_API_KEY` remains the only hosted NVIDIA NIM credential and is never exposed to the browser.
- Production statement and branch coverage remain exactly 100%.
- Every production public Python API retains a complete docstring.
- Existing calculation, idempotent enqueue, polling, download, deletion, and optional MSA contracts remain compatible.

---

### Task 1: Lock the browser history contract in failing tests

**Files:**
- Modify: `tests/test_web.py`

**Interfaces:**
- Consumes: `render_home() -> str`.
- Produces: required semantic markup and JavaScript hooks for history loading, filtering, pagination, polling, artifacts, privacy, and safe DOM rendering.

- [ ] **Step 1: Add semantic history markup assertions**

Require IDs:

```text
history
history-filter
history-refresh
history-status
history-list
history-more
```

Require a dedicated polite live region and visible privacy copy that states names, birth input, and notes are not displayed.

- [ ] **Step 2: Add behavior assertions**

Require source contracts for:

```javascript
async function loadHistory
new URLSearchParams
next_cursor
historyFilter.addEventListener('change'
historyRefresh.addEventListener('click'
historyMore.addEventListener('click'
loadHistory({reset:true})
```

Require artifact-link construction, active-job polling, and history refresh after successful enqueue.

- [ ] **Step 3: Add safe-DOM and ephemeral-state assertions**

Require `replaceChildren`, `textContent`, and `document.createElement`. Reject `innerHTML`, `localStorage`, `sessionStorage`, `indexedDB`, and cookie assignment.

- [ ] **Step 4: Run focused tests and verify RED**

```bash
pytest tests/test_web.py -v
```

Expected: history markup and behavior are absent.

- [ ] **Step 5: Commit the RED contract**

```bash
git add tests/test_web.py
git commit -m "test: require browser report history recovery"
```

### Task 2: Implement the Figma-backed responsive history panel

**Files:**
- Modify: `src/four_pillars/web.py`

**Interfaces:**
- Consumes: authenticated `GET /v1/reports`, `GET /v1/reports/{job_id}`, and existing allow-listed artifact URLs.
- Produces: safe `loadHistory({reset: boolean})`, row rendering, exact status filtering, cursor append, active-job restoration, and responsive presentation.

- [ ] **Step 1: Extend the existing visual system**

Add a full-width `.history-panel`, `.history-head`, `.history-controls`, `.history-list`, `.history-item`, `.history-chip`, `.history-meta`, and responsive mobile rules. Reuse existing navy, blue, coral, teal, gold, page, surface, muted, line, danger, and button tokens.

- [ ] **Step 2: Add semantic markup**

Place section 3 below the existing two-column workflow. Add native status select options for every `JobStatus`, refresh and load-more buttons, history list, privacy helper, and dedicated polite live region.

- [ ] **Step 3: Add ephemeral history state**

Track only:

```javascript
let historyCursor=null, historyLoading=false;
```

Keep the existing API key, calculation review, idempotency key, and polling state in memory only.

- [ ] **Step 4: Implement safe row rendering**

Build every node with `document.createElement`, `textContent`, and `replaceChildren`. Show localized status, shortened UUID, localized creation time, bounded error/status detail, and only server-supplied artifact links.

- [ ] **Step 5: Implement loading, filtering, and pagination**

`loadHistory({reset:true})` clears the cursor and rows, requests `limit=20`, and optionally adds exact status. A non-reset call supplies the current cursor and appends items. Show load more only when `next_cursor` exists.

- [ ] **Step 6: Integrate current-job workflow**

Queued and running rows restore the existing current-job panel and call `poll(job.id)`. Completed rows show artifact links. A successful report enqueue refreshes the first history page. Changing the API key and status filter reloads the first page.

- [ ] **Step 7: Implement explicit error and empty states**

Map HTTP 401 and 501 to the Korean product messages in the design spec. Show other bounded errors through `textContent`. Empty history receives a non-card message.

- [ ] **Step 8: Run focused tests and verify GREEN**

```bash
pytest tests/test_web.py -v
```

Expected: all browser source-contract tests pass.

- [ ] **Step 9: Commit the implementation**

```bash
git add src/four_pillars/web.py tests/test_web.py
git commit -m "feat: add browser report history recovery"
```

### Task 3: Document, verify, review, and merge

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `docs/product/PRD.md`
- Modify: `docs/technical/API.md`

**Interfaces:**
- Consumes: the complete Figma-backed browser implementation.
- Produces: a release-ready product increment and exact-head verification evidence.

- [ ] **Step 1: Update product and API documentation**

Document browser recovery, filtering, pagination, active-job restoration, privacy exclusions, authentication behavior, and the Figma source.

- [ ] **Step 2: Update `CHANGELOG.md`**

Record the browser history workflow under `Unreleased` without changing v0.5.0.

- [ ] **Step 3: Run the complete release-quality gate**

```bash
python -m pip check
python scripts/product_gap_audit.py
ruff check .
python -m compileall -q src tests scripts
python scripts/check_docs.py
python scripts/check_prompts.py
pytest -m 'not nim_live' -W error::ResourceWarning --cov=four_pillars --cov-report=term-missing
python -m build --no-isolation
docker build --tag four-pillars:browser-history .
```

Expected: all checks succeed, every production statement and branch is covered, and package/container builds succeed.

- [ ] **Step 4: Review against Figma and accessibility requirements**

Compare desktop and mobile information hierarchy, copy, palette, spacing, container model, status text, controls, and privacy copy with Figma nodes `2:3` and `2:136`. Resolve every code-review, security, and accessibility finding.

- [ ] **Step 5: Merge the exact green head**

Squash merge with an expected-head SHA guard only after CI, Security Scan, and Semgrep pass and no unresolved thread remains.
