from __future__ import annotations

import shutil
from pathlib import Path

from app.controller.batch import BatchProcessor
from app.controller.project_manager import ProjectManager
from app.data.models import Project
from app.engine.colors import ColorLibrary
from app.engine.csv_importer import CsvImporter
from app.engine.initials import InitialGenerator
from app.engine.templates import TemplateRegistry
from app.utils.logging import configure_logging


def test_sample_project_one_start_produces_outputs_reports_logs_and_progress(tmp_path: Path) -> None:
    project = _copy_sample_project(tmp_path)
    logger = configure_logging(project.root_path / "logs", "INFO")
    logger.info("Batch start")
    template = TemplateRegistry.load(project.root_path / "template" / "template.yaml")
    rows = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(
        project.root_path / "input" / "schools.csv"
    )

    result = BatchProcessor.default().start(project, template, rows)
    logger.info("Batch finish")

    assert result.failed == 0
    assert len(list((project.root_path / "output").glob("*.png"))) == len(rows)
    assert (project.root_path / "progress.json").exists()
    assert list((project.root_path / "reports").glob("*.html"))
    assert list((project.root_path / "logs").glob("*.log"))


def _copy_sample_project(tmp_path: Path) -> Project:
    source = Path("sample_project")
    root = tmp_path / "sample_project"
    shutil.copytree(source, root)
    project = ProjectManager().create_project("Sample Acceptance", root)
    project.template_id = "floral-varsity-sample"
    project.template_version = "1.0"
    project.csv_path = root / "input" / "schools.csv"
    project.output_path = root / "output"
    project.progress_path = root / "progress.json"
    ProjectManager().save_project(project)
    return project
