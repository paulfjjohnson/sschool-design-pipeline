from __future__ import annotations

from pathlib import Path

from app.data.models import Progress, Project
from app.data.serialization import read_json, write_json, write_yaml


class ProjectManager:
    required_directories = ("template", "input", "output", "logs", "qa", "reports", "backups")

    def create_project(self, name: str, root: Path) -> Project:
        root.mkdir(parents=True, exist_ok=True)
        for directory in self.required_directories:
            (root / directory).mkdir(parents=True, exist_ok=True)

        project = Project.new(project_name=name, root_path=root)
        project.output_path = root / "output"
        project.progress_path = root / "progress.json"
        write_json(root / "project.json", project)
        write_json(root / "progress.json", Progress())
        write_yaml(
            root / "settings.yaml",
            {
                "qa_profile": project.settings.qa_profile,
                "export_profile": project.settings.export_profile,
                "stop_on_failure": project.settings.stop_on_failure,
                "run_qa_before_export": project.settings.run_qa_before_export,
            },
        )
        return project

    def load_project(self, project_file: Path) -> Project:
        project = read_json(project_file, Project)
        project.root_path = project_file.parent
        if project.output_path is None:
            project.output_path = project.root_path / "output"
        if project.progress_path is None:
            project.progress_path = project.root_path / "progress.json"
        return project

    def save_project(self, project: Project) -> None:
        write_json(project.root_path / "project.json", project)

