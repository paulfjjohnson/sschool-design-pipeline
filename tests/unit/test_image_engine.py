from pathlib import Path

from app.engine.image_engine import LockedRegionComparator, PngTemplateEngine
from app.engine.templates import TemplateRegistry


def test_render_changes_only_registered_regions(
    sample_template_path: Path,
    sample_school,
) -> None:
    template = TemplateRegistry.load(sample_template_path)
    render = PngTemplateEngine(allow_default_font=True).render(template, sample_school)

    assert LockedRegionComparator(template).unexpected_changed_pixels(render.image) == 0
    assert render.image.mode == "RGBA"

