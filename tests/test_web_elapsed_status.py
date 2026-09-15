"""Tell the customer how long their report has been running.

The status line reads `상태: 실행 중` and never changes while the page polls
every two seconds. A job can stay in that state permanently, because nothing
reclaims an abandoned claim (#32): `claim_next` selects only `queued`, and both
`delete` and `purge` restrict themselves to terminal rows.

The page cannot know whether a worker is alive, and guessing a timeout would
tell a customer their healthy long report had died. Elapsed time needs no guess
and lets them judge for themselves, so it is what the page should show.
"""

from __future__ import annotations

from four_pillars.web import render_home


def test_the_running_status_reports_elapsed_time() -> None:
    """A static label gives a customer nothing to act on after ten minutes."""
    page = render_home()

    assert "elapsedLabel" in page


def test_elapsed_time_is_computed_from_the_job_the_server_returned() -> None:
    """It has to come from created_at, not from when this tab happened to open."""
    page = render_home()
    start = page.index("function elapsedLabel")
    body = page[start : page.index("\n", start)]

    assert "created_at" in body


def test_the_status_line_uses_it() -> None:
    """Computing it without showing it would change nothing for the customer."""
    page = render_home()
    poll_start = page.index("async function poll(")
    poll_body = page[poll_start : page.index("\n", poll_start)]

    assert "elapsedLabel(" in poll_body
