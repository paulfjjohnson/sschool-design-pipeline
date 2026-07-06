from pathlib import Path

from app.controller.project_manager import ProjectManager
from app.controller.progress import ProgressService
from app.data.models import QAResult, SchoolRecord


def test_project_resume_finds_first_incomplete_after_reload(tmp_path: Path) -> None:
    project = ProjectManager().create_project("Resume Test", tmp_path)
    rows = [SchoolRecord.example(1), SchoolRecord.example(2), SchoolRecord.example(3)]
    progress = ProgressService(project.progress_path)

    progress.mark_completed(rows[0], QAResult.passed_for(rows[0]))
    progress.mark_failed(rows[1])

    reloaded = ProjectManager().load_project(tmp_path / "project.json")
    restored_progress = ProgressService(reloaded.progress_path)

    assert restored_progress.first_incomplete(rows) == 2
