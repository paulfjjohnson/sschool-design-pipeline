from pathlib import Path

import pytest

from app.config.manager import ConfigurationManager
from app.controller.app_controller import ApplicationController
from app.data.models import SchoolRecord
from app.engine.image_engine import PngTemplateEngine
from app.engine.templates import TemplateRegistry
from app.main import main
from app.qa.rules import RuleOutcome
from app.qa.service import QAService
from app.utils.paths import ensure_directory, sanitize_filename


def test_main_version_outputs_version(capsys) -> None:
    assert main(["--version"]) == 0
    assert "0.1.0" in capsys.readouterr().out


def test_configuration_rejects_invalid_runtime_values() -> None:
    manager = ConfigurationManager(Path("app/config/defaults.yaml"))

    with pytest.raises(ValueError, match="DPI"):
        manager.load({"default_dpi": 0})


def test_path_helpers_create_dirs_and_sanitize_reserved_names(tmp_path: Path) -> None:
    created = ensure_directory(tmp_path / "nested")

    assert created.exists()
    assert sanitize_filename("CON") == "CON_file.png"
    assert sanitize_filename("Pecan Grove Primary") == "Pecan_Grove_Primary.png"


def test_qa_fails_when_locked_pixels_change(sample_template_path: Path, sample_school) -> None:
    template = TemplateRegistry.load(sample_template_path)
    render = PngTemplateEngine(allow_default_font=True).render(template, sample_school)
    render.image.putpixel((2, 2), (255, 0, 0, 255))

    qa = QAService().validate(render, sample_school)

    assert qa.passed is False
    assert "Locked pixels changed" in " ".join(qa.failures)


def test_rule_outcome_holds_rule_status() -> None:
    outcome = RuleOutcome("geometry", "Passed", "ok")

    assert outcome.name == "geometry"


def test_application_controller_loads_project_template_csv_and_starts(tmp_path: Path) -> None:
    controller = ApplicationController()
    project = controller.new_project("Controller", tmp_path)
    template = controller.load_template(Path("sample_project/template/template.yaml"))
    queue = controller.load_csv(Path("sample_project/input/schools.csv"))

    result = controller.start_batch()

    assert project.project_name == "Controller"
    assert template.name == "Floral Varsity Sample"
    assert len(queue) == 4
    assert result.completed == 4
    assert len(list(project.output_path.glob("*.png"))) == 4


def test_application_controller_reopens_project_inputs(tmp_path: Path) -> None:
    controller = ApplicationController()
    project = controller.new_project("Reopen", tmp_path)
    template_dir = project.root_path / "template"
    import shutil

    shutil.copytree(Path("sample_project/template"), template_dir, dirs_exist_ok=True)
    csv_path = project.root_path / "input" / "schools.csv"
    shutil.copy2(Path("sample_project/input/schools.csv"), csv_path)
    controller.load_template(template_dir / "template.yaml")
    controller.load_csv(csv_path)

    reopened = ApplicationController()
    reopened.open_project(project.root_path / "project.json")

    assert reopened.template is not None
    assert reopened.queue

