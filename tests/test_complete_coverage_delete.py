from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from four_pillars import api as api_module
from four_pillars.jobs import JobStore
from four_pillars.service import ReportService
from four_pillars.settings import Settings


def test_delete_report_rejects_an_unknown_job(tmp_path: Path) -> None:
    """Return an HTTP 404 when deletion targets a missing report job."""
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    service = ReportService(settings, JobStore(settings.sqlite_path))

    with pytest.raises(HTTPException) as captured:
        api_module.delete_report("missing", service)

    assert captured.value.status_code == 404
