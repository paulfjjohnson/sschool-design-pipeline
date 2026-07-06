from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageColor, ImageOps

from app.data.models import SchoolRecord, Template
from app.engine.templates import TemplateValidationError
from app.engine.typography import TextRenderer
from app.engine.colors import ColorLibrary


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

        self._replace_pattern_initials(image, template, record.initials, record.color_primary, record.color_secondary)
        self._replace_text(image, template, "script", _apply_case(record.school_name, template.script_case),
                           (*ImageColor.getrgb(_color_to_hex(record.color_primary)), 255))
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

    def _replace_pattern_initials(
        self, image: Image.Image, template: Template, text: str, outline_color: str, pattern_color: str
    ) -> None:
        target = _region(template, "initials")
        floral = _region(template, "floral")
        target_mask = Image.open(target.mask_path).convert("L") if target.mask_path else _box_mask(image.size, target)
        glyph = TextRenderer(template.default_font, allow_default_font=self.allow_default_font).render_text(
            text, (target.width, target.height), fill=(255, 255, 255, 255)
        )
        alpha = np.array(glyph.getchannel("A"))
        contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        silhouette = np.zeros_like(alpha)
        cv2.drawContours(silhouette, contours, -1, 255, thickness=cv2.FILLED)
        silhouette_image = Image.fromarray(silhouette, mode="L")

        if template.pattern_path:
            source = Image.open(template.pattern_path).convert("RGBA")
        else:
            source = Image.open(template.source_path).convert("RGBA").crop(
                (floral.x, floral.y, floral.x + floral.width, floral.y + floral.height)
            )
        if source.width == 0 or source.height == 0:
            raise TemplateValidationError("Floral pattern source region is empty.")
        tiled = Image.new("RGBA", (target.width, target.height))
        for y in range(0, target.height, source.height):
            for x in range(0, target.width, source.width):
                tile = source
                if (x // source.width) % 2:
                    tile = ImageOps.mirror(tile)
                if (y // source.height) % 2:
                    tile = ImageOps.flip(tile)
                tiled.alpha_composite(tile, (x, y))
        if template.pattern_treatment == "tint":
            rgb = ImageColor.getrgb(_color_to_hex(pattern_color))
            gray = ImageOps.grayscale(tiled)
            textured = ImageOps.colorize(
                gray, black=tuple(max(0, value // 3) for value in rgb), white=rgb
            ).convert("RGBA")
        else:
            textured = tiled.copy()
        textured.putalpha(silhouette_image)
        outline = Image.new("RGBA", glyph.size, (*ImageColor.getrgb(_color_to_hex(outline_color)), 0))
        outline.putalpha(glyph.getchannel("A"))
        textured.alpha_composite(outline)

        image.paste(Image.new("RGBA", image.size), (0, 0), target_mask)
        patch = Image.new("RGBA", image.size)
        patch.alpha_composite(textured, (target.x, target.y))
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
    return ColorLibrary.default().resolve(color_name).hex


def _apply_case(value: str, mode: str) -> str:
    transforms = {"title": str.title, "upper": str.upper, "lower": str.lower}
    return transforms.get(mode, lambda text: text)(value)
