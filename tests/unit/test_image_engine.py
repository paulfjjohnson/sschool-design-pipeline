from pathlib import Path

from app.engine.image_engine import LockedRegionComparator, PngTemplateEngine
from app.engine.templates import TemplateRegistry
from app.engine.image_engine import _apply_case, _filled_glyph_silhouette
import numpy as np


def test_render_changes_only_registered_regions(
    sample_template_path: Path,
    sample_school,
) -> None:
    template = TemplateRegistry.load(sample_template_path)
    render = PngTemplateEngine(allow_default_font=True).render(template, sample_school)

    assert LockedRegionComparator(template).unexpected_changed_pixels(render.image) == 0
    assert render.image.mode == "RGBA"


def test_script_case_modes() -> None:
    assert _apply_case("bluff ridge primary", "title") == "Bluff Ridge Primary"
    assert _apply_case("Bluff Ridge Primary", "upper") == "BLUFF RIDGE PRIMARY"
    assert _apply_case("Bluff Ridge Primary", "lower") == "bluff ridge primary"
    assert _apply_case("Bluff Ridge Primary", "as_entered") == "Bluff Ridge Primary"


def test_pattern_fill_retains_texture_variation(sample_template_path: Path, sample_school) -> None:
    template = TemplateRegistry.load(sample_template_path)
    rendered = PngTemplateEngine(allow_default_font=True).render(template, sample_school).image
    crop = rendered.crop((20, 20, 130, 80)).convert("RGB")
    assert len(crop.getcolors(maxcolors=100_000) or []) > 3


def test_filled_glyph_silhouette_preserves_enclosed_letter_holes() -> None:
    ring = np.zeros((60, 60), dtype=np.uint8)
    ring[3:57, 3:57] = 255
    ring[8:52, 8:52] = 0
    ring[18:42, 18:42] = 255
    ring[24:36, 24:36] = 0

    silhouette = _filled_glyph_silhouette(ring)

    assert silhouette[12, 12] == 255
    assert silhouette[29, 29] == 0

