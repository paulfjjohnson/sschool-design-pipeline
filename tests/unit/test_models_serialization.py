from pathlib import Path

from app.data.models import Project
from app.data.serialization import read_json, write_json


def test_project_round_trips_json(tmp_path: Path) -> None:
    project = Project.new(project_name="Ascension Primary", root_path=tmp_path)
    path = tmp_path / "project.json"

    write_json(path, project)
    loaded = read_json(path, Project)

    assert loaded.project_id == project.project_id
    assert loaded.project_name == "Ascension Primary"
    assert loaded.root_path == tmp_path

