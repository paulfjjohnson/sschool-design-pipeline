from pathlib import Path

from app.controller.project_manager import ProjectManager


def test_project_manager_creates_portable_structure(tmp_path: Path) -> None:
    project = ProjectManager().create_project("Ascension", tmp_path)

    assert (tmp_path / "project.json").exists()
    assert (tmp_path / "progress.json").exists()
    assert (tmp_path / "settings.yaml").exists()
    assert (tmp_path / "output").is_dir()
    assert (tmp_path / "qa").is_dir()
    assert (tmp_path / "reports").is_dir()
    assert project.project_name == "Ascension"


def test_project_manager_loads_project(tmp_path: Path) -> None:
    manager = ProjectManager()
    created = manager.create_project("Ascension", tmp_path)

    loaded = manager.load_project(tmp_path / "project.json")

    assert loaded.project_id == created.project_id
    assert loaded.root_path == tmp_path

