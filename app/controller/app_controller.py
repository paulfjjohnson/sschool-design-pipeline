from __future__ import annotations

from pathlib import Path

from app.controller.batch import BatchProcessor, BatchResult
from app.controller.project_manager import ProjectManager
from app.data.models import Project, SchoolRecord, Template
from app.engine.colors import ColorLibrary
from app.engine.csv_importer import CsvImporter
from app.engine.initials import InitialGenerator
from app.engine.templates import TemplateRegistry
from app.engine.tabular_importer import TabularImporter
from app.data.models import QAStatus, SchoolStatus
from app.utils.logging import configure_logging


class ApplicationController:
    def __init__(self) -> None:
        self.project_manager = ProjectManager()
        self.batch_processor = BatchProcessor.default()
        self.project: Project | None = None
        self.template: Template | None = None
        self.queue: list[SchoolRecord] = []
        self.logger = None

    @classmethod
    def fake(cls) -> ApplicationController:
        return cls()

    def new_project(self, name: str, root: Path) -> Project:
        self.project = self.project_manager.create_project(name, root)
        self.logger = configure_logging(root / "logs", "INFO")
        self.logger.info("Project created: %s", name)
        return self.project

    def open_project(self, path: Path) -> Project:
        self.project = self.project_manager.load_project(path)
        self.logger = configure_logging(self.project.root_path / "logs", "INFO")
        self.logger.info("Project opened")
        metadata_path = self.project.root_path / "template" / "template.yaml"
        if metadata_path.exists():
            self.template = TemplateRegistry.load(metadata_path)
        if self.project.csv_path and self.project.csv_path.exists():
            self.queue = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(self.project.csv_path)
        return self.project

    def load_template(self, path: Path) -> Template:
        self.template = TemplateRegistry.load(path)
        if self.project:
            self.project.template_id = self.template.template_id
            self.project.template_version = self.template.version
            self.project_manager.save_project(self.project)
        return self.template

    def load_csv(self, path: Path) -> list[SchoolRecord]:
        if path.suffix.lower() == ".xlsx" or (self.template and self.template.schema_version.startswith("2")):
            batch = TabularImporter().import_file(path)
            self.queue = []
            for index, values in enumerate(batch.rows, 1):
                name = values.get("School") or values.get("Name") or values.get("Display Name") or f"Item {index}"
                initials = InitialGenerator().generate(name).initials
                values.setdefault("Generated Initials", initials)
                self.queue.append(SchoolRecord(index, name, values.get("Mascot", ""),
                    values.get("Color 1", "Black"), values.get("Color 2", "White"), initials,
                    f"{name.replace(' ', '_')}_{self.template.name if self.template else 'Collection'}.png",
                    source_values=values))
        else:
            self.queue = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(path)
        if self.project:
            self.project.csv_path = path
            self.project_manager.save_project(self.project)
        return self.queue

    def start_batch(self) -> BatchResult:
        if self.project is None or self.template is None:
            raise RuntimeError("Project and template must be loaded before starting.")
        if self.logger:
            self.logger.info("Batch started with %d rows", len(self.queue))
        result = self.batch_processor.start(self.project, self.template, self.queue)
        if self.logger:
            self.logger.info(
                "Batch finished: %d completed, %d failed, %d skipped",
                result.completed,
                result.failed,
                result.skipped,
            )
        return result

    def rebuild_all(self) -> BatchResult:
        if self.project is None or self.template is None:
            raise RuntimeError("Project and template must be loaded before rebuilding.")
        return self.batch_processor.rebuild_all(self.project, self.template, self.queue)

