from pathlib import Path

from app.controller.batch import BatchProcessor
from app.controller.project_manager import ProjectManager
from app.data.models import SchoolStatus
from app.engine.colors import ColorLibrary
from app.engine.csv_importer import CsvImporter
from app.engine.initials import InitialGenerator
from app.engine.templates import TemplateRegistry


def test_batch_processes_valid_rows_and_writes_progress(tmp_path: Path) -> None:
    project = ProjectManager().create_project("Batch", tmp_path)
    template = TemplateRegistry.load(Path("sample_project/template/template.yaml"))
    rows = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(
        Path("sample_project/input/schools.csv")
    )

    result = BatchProcessor.default().start(project, template, rows)

    assert result.completed == len(rows)
    assert project.progress_path.exists()
    assert len(list(project.output_path.glob("*.png"))) == len(rows)
    assert (tmp_path / "reports" / "batch_summary.html").exists()


def test_completed_rows_are_not_regenerated_on_resume(tmp_path: Path) -> None:
    project = ProjectManager().create_project("Resume Batch", tmp_path)
    template = TemplateRegistry.load(Path("sample_project/template/template.yaml"))
    rows = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(
        Path("sample_project/input/schools.csv")
    )
    processor = BatchProcessor.default()

    first = processor.start(project, template, rows[:1])
    second = processor.start(project, template, rows)

    assert first.completed == 1
    assert second.skipped_completed == 1
    assert second.completed == len(rows) - 1


def test_needs_review_rows_are_failed_not_exported(tmp_path: Path) -> None:
    project = ProjectManager().create_project("Review Batch", tmp_path)
    template = TemplateRegistry.load(Path("sample_project/template/template.yaml"))
    rows = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(
        Path("sample_project/input/schools.csv")
    )
    rows[0].status = SchoolStatus.NEEDS_REVIEW
    rows[0].notes = "Manual initials review required."

    result = BatchProcessor.default().start(project, template, rows)

    assert result.failed == 1
    assert not (project.output_path / rows[0].export_filename).exists()

