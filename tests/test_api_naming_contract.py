"""Naming-contract tests for Four Pillars report-job API models."""

from datetime import datetime, timezone

from four_pillars.api import ReportJobPageView, ReportJobView
from four_pillars.models import JobStatus


def test_report_job_view_uses_specific_owned_names_with_legacy_wire_aliases() -> None:
    """Require semantic Python names while preserving the established JSON keys."""
    observed_at = datetime(2026, 9, 2, tzinfo=timezone.utc)
    report_job = ReportJobView(
        report_job_id="11111111-1111-4111-8111-111111111111",
        job_status=JobStatus.QUEUED,
        created_at=observed_at,
        updated_at=observed_at,
        job_error_message=None,
        artifact_names=[],
    )

    assert set(ReportJobView.model_fields) == {
        "report_job_id",
        "job_status",
        "created_at",
        "updated_at",
        "job_error_message",
        "artifact_names",
    }
    assert {"id", "status", "error", "artifacts"}.isdisjoint(ReportJobView.model_fields)
    assert report_job.model_dump(by_alias=True, mode="json") == {
        "id": "11111111-1111-4111-8111-111111111111",
        "status": "queued",
        "created_at": "2026-09-02T00:00:00Z",
        "updated_at": "2026-09-02T00:00:00Z",
        "error": None,
        "artifacts": [],
    }


def test_report_job_page_uses_specific_collection_name_and_accepts_legacy_wire() -> None:
    """Keep the owned page collection semantic without breaking existing clients."""
    legacy_payload = {
        "items": [
            {
                "id": "22222222-2222-4222-8222-222222222222",
                "status": "completed",
                "created_at": "2026-09-02T00:00:00Z",
                "updated_at": "2026-09-02T00:01:00Z",
                "error": None,
                "artifacts": ["report.json"],
            }
        ],
        "next_cursor": None,
    }

    report_page = ReportJobPageView.model_validate(legacy_payload)

    assert set(ReportJobPageView.model_fields) == {"report_jobs", "next_cursor"}
    assert "items" not in ReportJobPageView.model_fields
    assert report_page.report_jobs[0].report_job_id == "22222222-2222-4222-8222-222222222222"
    assert report_page.model_dump(by_alias=True, mode="json") == legacy_payload
