from pathlib import Path

import pytest

from app.controller.progress import ProgressService, ProgressStateError
from app.data.models import QAResult, SchoolRecord


def test_progress_resumes_at_first_incomplete(tmp_path: Path) -> None:
    progress = ProgressService(tmp_path / "progress.json")
    rows = [SchoolRecord.example(row_number=1), SchoolRecord.example(row_number=2)]

    progress.mark_completed(rows[0], QAResult.passed_for(rows[0]))

    assert progress.first_incomplete(rows) == 1


def test_progress_does_not_lose_failed_rows(tmp_path: Path) -> None:
    progress = ProgressService(tmp_path / "progress.json")
    row = SchoolRecord.example(row_number=7)

    progress.mark_failed(row)
    loaded = progress.load()

    assert loaded.failed_rows == [7]


def test_corrupt_progress_file_raises_state_error(tmp_path: Path) -> None:
    path = tmp_path / "progress.json"
    path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(ProgressStateError):
        ProgressService(path).load()


def test_reset_clears_all_resume_state(tmp_path: Path) -> None:
    service = ProgressService(tmp_path / "progress.json")
    row = SchoolRecord.example(1)
    service.mark_completed(row, QAResult.passed_for(row))

    service.reset()

    assert service.load().completed_rows == []

