from pathlib import Path

from app.data.models import QAStatus
from app.engine.image_engine import PngTemplateEngine
from app.engine.templates import TemplateRegistry
from app.qa.service import QAService


def test_qa_passes_valid_render(sample_template_path: Path, sample_school) -> None:
    template = TemplateRegistry.load(sample_template_path)
    render = PngTemplateEngine(allow_default_font=True).render(template, sample_school)
    qa = QAService().validate(render, sample_school)

    assert qa.passed is True
    assert qa.geometry_check is QAStatus.PASSED
    assert qa.transparency_check is QAStatus.PASSED

