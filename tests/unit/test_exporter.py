from pathlib import Path

import pytest
from PIL import Image

from app.data.models import QAResult
from app.engine.image_engine import PngTemplateEngine
from app.engine.templates import TemplateRegistry
from app.export.exporter import PngExporter
from app.utils.errors import QABlockedExportError


def test_qa_failure_blocks_export(
    tmp_path: Path,
    sample_template_path: Path,
    sample_school,
) -> None:
    template = TemplateRegistry.load(sample_template_path)
    render = PngTemplateEngine(allow_default_font=True).render(template, sample_school)
    qa = QAResult.failed_for(sample_school, "geometry", "Geometry checksum mismatch")

    with pytest.raises(QABlockedExportError):
        PngExporter().export(render, sample_school, tmp_path, qa)


def test_png_export_has_alpha_and_300_dpi(
    tmp_path: Path,
    sample_template_path: Path,
    sample_school,
) -> None:
    template = TemplateRegistry.load(sample_template_path)
    render = PngTemplateEngine(allow_default_font=True).render(template, sample_school)
    qa = QAResult.passed_for(sample_school)

    path = PngExporter().export(render, sample_school, tmp_path, qa)

    image = Image.open(path)
    assert image.mode == "RGBA"
    assert image.info["dpi"][0] == pytest.approx(300, abs=1)
    assert image.info["dpi"][1] == pytest.approx(300, abs=1)

