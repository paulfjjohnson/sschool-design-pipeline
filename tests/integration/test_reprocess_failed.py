from pathlib import Path

from app.controller.batch import BatchProcessor
from app.controller.project_manager import ProjectManager
from app.data.models import SchoolStatus
from app.engine.csv_importer import CsvImporter
from app.engine.colors import ColorLibrary
from app.engine.initials import InitialGenerator
from app.engine.templates import TemplateRegistry


def test_reprocess_failed_processes_fixed_rows(tmp_path: Path) -> None:
    project = ProjectManager().create_project("Reprocess", tmp_path)
    template = TemplateRegistry.load(Path("sample_project/template/template.yaml"))
    rows = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(
        Path("sample_project/input/schools.csv")
    )
    rows[0].status = SchoolStatus.NEEDS_REVIEW
    processor = BatchProcessor.default()

    first = processor.start(project, template, rows)
    rows[0].status = SchoolStatus.PENDING
    rows[0].notes = ""
    second = processor.reprocess_failed(project, template, rows)

    assert first.failed == 1
    assert second.completed >= 1
    assert (project.output_path / rows[0].export_filename).exists()

