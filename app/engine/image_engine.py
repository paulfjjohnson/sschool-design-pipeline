from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageColor

from app.data.models import SchoolRecord, Template
from app.engine.templates import TemplateValidationError
from app.engine.typography import TextRenderer


@dataclass(frozen=True, slots=True)
class RenderResult:
    image: Image.Image
    template: Template
    record: SchoolRecord
    changed_mask: Image.Image


class PngTemplateEngine:
    def __init__(self, allow_default_font: bool = False) -> None:
        self.allow_default_font = allow_default_font

    def render(self, template: Template, record: SchoolRecord) -> RenderResult:
        if template.format != "PNG":
            raise TemplateValidationError("PNG template engine can only render PNG templates.")
        image = Image.open(template.source_path).convert("RGBA")
        changed_mask = _combined_mask(template).convert("L")

        self._replace_text(image, template, "initials", record.initials, (255, 255, 255, 255))
        self._replace_text(image, template, "script", record.school_name, (255, 255, 255, 255))
        self._recolor_region(image, template, "outline", record.color_primary)
        self._recolor_region(image, template, "floral", record.color_secondary)
        return RenderResult(image=image, template=template, record=record, changed_mask=changed_mask)

    def _replace_text(
        self,
        image: Image.Image,
        template: Template,
        region_name: str,
        text: str,
        fill: tuple[int, int, int, int],
    ) -> None:
        region = _region(template, region_name)
        mask = Image.open(region.mask_path).convert("L") if region.mask_path else _box_mask(image.size, region)
        replacement = TextRenderer(
            template.default_font if region_name == "initials" else template.script_font,
            allow_default_font=self.allow_default_font,
        ).render_text(text, (region.width, region.height), fill=fill)
        patch = Image.new("RGBA", image.size, (0, 0, 0, 0))
        patch.alpha_composite(replacement, (region.x, region.y))
        clear = Image.new("RGBA", image.size, (0, 0, 0, 0))
        image.paste(clear, (0, 0), mask)
        image.alpha_composite(patch)

    def _recolor_region(self, image: Image.Image, template: Template, region_name: str, color_name: str) -> None:
        region = _region(template, region_name)
        mask = Image.open(region.mask_path).convert("L") if region.mask_path else _box_mask(image.size, region)
        rgb = ImageColor.getrgb(_color_to_hex(color_name))
        solid = Image.new("RGBA", image.size, (*rgb, 255))
        alpha = image.getchannel("A")
        constrained_mask = ImageChops.multiply(mask, alpha)
        image.paste(solid, (0, 0), constrained_mask)


class LockedRegionComparator:
    def __init__(self, template: Template) -> None:
        self.template = template
        self.master = Image.open(template.source_path).convert("RGBA")
        self.editable_mask = _combined_mask(template).convert("L")

    def unexpected_changed_pixels(self, rendered: Image.Image) -> int:
        rendered = rendered.convert("RGBA")
        diff = ImageChops.difference(self.master, rendered)
        diff_alpha = diff.convert("L").point(lambda value: 255 if value else 0)
        locked_mask = self.editable_mask.point(lambda value: 0 if value else 255)
        unexpected = ImageChops.multiply(diff_alpha, locked_mask)
        histogram = unexpected.histogram()
        return sum(histogram[1:])


def _region(template: Template, name: str):
    for region in template.editable_regions:
        if region.name == name:
            return region
    raise TemplateValidationError(f"Missing editable region: {name}")


def _combined_mask(template: Template) -> Image.Image:
    base = Image.open(template.source_path).convert("RGBA")
    combined = Image.new("L", base.size, 0)
    for region in template.editable_regions:
        mask = Image.open(region.mask_path).convert("L") if region.mask_path else _box_mask(base.size, region)
        combined = ImageChops.lighter(combined, mask)
    return combined


def _box_mask(size: tuple[int, int], region) -> Image.Image:
    mask = Image.new("L", size, 0)
    from PIL import ImageDraw

    ImageDraw.Draw(mask).rectangle(
        (region.x, region.y, region.x + region.width, region.y + region.height),
        fill=255,
    )
    return mask


def _color_to_hex(color_name: str) -> str:
    palette = {
        "red": "#C8102E",
        "royal": "#0057B8",
        "royal blue": "#0057B8",
        "green": "#00843D",
        "yellow": "#FFD100",
        "gold": "#FFD100",
        "white": "#FFFFFF",
        "black": "#000000",
        "navy": "#00205B",
    }
    return palette.get(color_name.strip().lower(), "#000000")
