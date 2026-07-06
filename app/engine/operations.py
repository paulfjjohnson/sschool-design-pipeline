from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFont, ImageOps

from app.data.models import OperationType, Template, TemplateOperation
from app.engine.assets import AssetResolver
from app.engine.colors import ColorLibrary
from app.engine.typography import TextRenderer


class OperationRenderer:
    def render(self, template: Template, row: dict[str, str], spreadsheet_path: Path) -> Image.Image:
        image = Image.open(template.source_path).convert("RGBA")
        for operation in sorted(template.operations, key=lambda item: item.layer_order):
            self._apply(image, template, operation, row, spreadsheet_path)
        return image

    def _apply(self, image: Image.Image, template: Template, operation: TemplateOperation,
               row: dict[str, str], spreadsheet_path: Path) -> None:
        if operation.operation_type is OperationType.LOCKED:
            return
        value = operation.default_value or ""
        if operation.column and operation.allow_override and row.get(operation.column, "").strip():
            value = row[operation.column].strip()
        if operation.required and not value:
            raise ValueError(f"{operation.name}: required value is missing from {operation.column}.")
        mask = self._mask(image.size, operation)
        box = (operation.x, operation.y, operation.x + operation.width, operation.y + operation.height)
        if operation.operation_type is OperationType.VISIBILITY:
            if value.lower() not in {"1", "true", "yes", "y", "show"}:
                image.paste(Image.new("RGBA", image.size), (0, 0), mask)
            return
        if operation.operation_type is OperationType.SOLID_COLOR:
            color = ColorLibrary.default().resolve(value).hex
            image.paste(Image.new("RGBA", image.size, (*ImageColor.getrgb(color), 255)), (0, 0), mask)
            return
        if operation.operation_type is OperationType.TEXT:
            case = operation.config.get("case", "as_entered")
            value = {"upper": str.upper, "lower": str.lower, "title": str.title}.get(case, lambda x: x)(value)
            font_path = Path(operation.config["font_path"]) if operation.config.get("font_path") else template.default_font
            color_value = row.get(operation.config.get("color_column", ""), operation.config.get("color", "Black"))
            color = ColorLibrary.default().resolve(color_value).hex
            patch = TextRenderer(font_path).render_text(value, (operation.width, operation.height),
                                                        fill=(*ImageColor.getrgb(color), 255))
            image.paste(Image.new("RGBA", image.size), (0, 0), mask)
            image.alpha_composite(patch, (operation.x, operation.y))
            return
        if operation.operation_type is OperationType.PATTERN_TEXT:
            patch = self._render_pattern_text(template, operation, value, row, spreadsheet_path)
            image.paste(Image.new("RGBA", image.size), (0, 0), mask)
            image.alpha_composite(patch, (operation.x, operation.y))
            return
        if operation.operation_type in {OperationType.IMAGE_REPLACE, OperationType.PATTERN_FILL}:
            if operation.operation_type is OperationType.PATTERN_FILL and not value and template.pattern_path:
                asset = template.pattern_path
            else:
                asset = AssetResolver().resolve(value, spreadsheet_path)
            source = Image.open(asset).convert("RGBA")
            if operation.operation_type is OperationType.PATTERN_FILL:
                fitted = Image.new("RGBA", (operation.width, operation.height))
                for y in range(0, operation.height, source.height):
                    for x in range(0, operation.width, source.width):
                        fitted.alpha_composite(source, (x, y))
            else:
                fitted = self._fit(source, (operation.width, operation.height), operation.config.get("fit", "contain"))
            canvas = Image.new("RGBA", image.size)
            canvas.alpha_composite(fitted, (operation.x, operation.y))
            image.paste(canvas, (0, 0), mask)

    def _render_pattern_text(
        self,
        template: Template,
        operation: TemplateOperation,
        value: str,
        row: dict[str, str],
        spreadsheet_path: Path,
    ) -> Image.Image:
        case = operation.config.get("case", "as_entered")
        text = {"upper": str.upper, "lower": str.lower, "title": str.title}.get(case, lambda x: x)(value)
        font_path = Path(operation.config["font_path"]) if operation.config.get("font_path") else template.default_font
        font = self._load_font(font_path, text, (operation.width, operation.height))
        outline_width = int(operation.config.get("outline_width", max(1, min(operation.width, operation.height) // 28)))
        fill_mask = self._text_mask(text, font, (operation.width, operation.height), 0)
        stroke_mask = self._text_mask(text, font, (operation.width, operation.height), outline_width)
        outline_mask = ImageChops.subtract(stroke_mask, fill_mask)
        outline_color = self._resolve_configured_color(operation, row, "outline_color_column", "outline_color", "Black")
        pattern = self._load_pattern(template, operation, row, spreadsheet_path)
        pattern = self._scale_pattern(pattern, float(operation.config.get("pattern_scale", 1.0)))
        pattern = self._tile(pattern, (operation.width, operation.height))
        pattern_treatment = operation.config.get("pattern_treatment")
        if pattern_treatment in {"tint_nonwhite", "tint_saturated"}:
            color = self._resolve_configured_color(operation, row, "pattern_color_column", "pattern_color", "Black")
            pattern = self._tint_saturated(pattern, color) if pattern_treatment == "tint_saturated" else self._tint_nonwhite(pattern, color)
        patch = Image.new("RGBA", (operation.width, operation.height), (0, 0, 0, 0))
        outline_layer = Image.new("RGBA", patch.size, (*ImageColor.getrgb(outline_color), 255))
        patch.paste(outline_layer, (0, 0), outline_mask)
        patch.paste(pattern, (0, 0), fill_mask)
        return patch

    @staticmethod
    def _resolve_configured_color(
        operation: TemplateOperation,
        row: dict[str, str],
        column_key: str,
        value_key: str,
        fallback: str,
    ) -> str:
        color_value = operation.config.get(value_key, fallback)
        column = operation.config.get(column_key)
        if column and row.get(column, "").strip():
            color_value = row[column].strip()
        return ColorLibrary.default().resolve(color_value).hex

    @staticmethod
    def _load_font(font_path: Path | None, text: str, size: tuple[int, int]) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
        max_width, max_height = size
        text_length = max(1, len(text))
        font_size = max(10, min(max_height - 4, max_width // text_length * 2))
        if font_path and font_path.exists():
            for candidate in range(font_size, 9, -2):
                font = ImageFont.truetype(str(font_path), candidate)
                bbox = ImageDraw.Draw(Image.new("L", size)).textbbox((0, 0), text, font=font, stroke_width=0)
                if bbox[2] - bbox[0] <= max_width - 4 and bbox[3] - bbox[1] <= max_height - 4:
                    return font
            return ImageFont.truetype(str(font_path), 10)
        return ImageFont.load_default(font_size)

    @staticmethod
    def _text_mask(
        text: str,
        font: ImageFont.ImageFont | ImageFont.FreeTypeFont,
        size: tuple[int, int],
        stroke_width: int,
    ) -> Image.Image:
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = max(0, (size[0] - text_width) // 2 - bbox[0])
        y = max(0, (size[1] - text_height) // 2 - bbox[1])
        draw.text((x, y), text, font=font, fill=255, stroke_width=stroke_width, stroke_fill=255)
        return mask

    @staticmethod
    def _load_pattern(
        template: Template,
        operation: TemplateOperation,
        row: dict[str, str],
        spreadsheet_path: Path,
    ) -> Image.Image:
        pattern_value = operation.config.get("pattern_path") or operation.default_value or ""
        pattern_column = operation.config.get("pattern_column")
        if pattern_column and row.get(pattern_column, "").strip():
            pattern_value = row[pattern_column].strip()
        if pattern_value:
            return Image.open(AssetResolver().resolve(pattern_value, spreadsheet_path)).convert("RGBA")
        if template.pattern_path:
            return Image.open(template.pattern_path).convert("RGBA")
        raise ValueError(f"{operation.name}: pattern text requires a pattern_path, default value, or template pattern.")

    @staticmethod
    def _tile(source: Image.Image, size: tuple[int, int]) -> Image.Image:
        fitted = Image.new("RGBA", size)
        for y in range(0, size[1], source.height):
            for x in range(0, size[0], source.width):
                fitted.alpha_composite(source, (x, y))
        return fitted

    @staticmethod
    def _scale_pattern(source: Image.Image, scale: float) -> Image.Image:
        if scale <= 0:
            raise ValueError("pattern_scale must be greater than 0.")
        if scale == 1:
            return source
        width = max(1, int(round(source.width * scale)))
        height = max(1, int(round(source.height * scale)))
        return source.resize((width, height), Image.Resampling.LANCZOS)

    @staticmethod
    def _tint_nonwhite(source: Image.Image, color: str) -> Image.Image:
        target = ImageColor.getrgb(color)
        tinted = source.copy()
        pixels = tinted.load()
        for y in range(tinted.height):
            for x in range(tinted.width):
                red, green, blue, alpha = pixels[x, y]
                if alpha and min(red, green, blue) < 245:
                    pixels[x, y] = (*target, alpha)
        return tinted

    @staticmethod
    def _tint_saturated(source: Image.Image, color: str) -> Image.Image:
        target = ImageColor.getrgb(color)
        tinted = source.copy()
        pixels = tinted.load()
        for y in range(tinted.height):
            for x in range(tinted.width):
                red, green, blue, alpha = pixels[x, y]
                spread = max(red, green, blue) - min(red, green, blue)
                darkness = 255 - max(red, green, blue)
                if alpha and (spread >= 25 or darkness >= 35):
                    pixels[x, y] = (*target, alpha)
        return tinted

    @staticmethod
    def _mask(size: tuple[int, int], operation: TemplateOperation) -> Image.Image:
        if operation.mask_path:
            return Image.open(operation.mask_path).convert("L")
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).rectangle(
            (operation.x, operation.y, operation.x + operation.width - 1, operation.y + operation.height - 1), fill=255
        )
        return mask

    @staticmethod
    def _fit(source: Image.Image, size: tuple[int, int], mode: str) -> Image.Image:
        if mode == "stretch":
            return source.resize(size, Image.Resampling.LANCZOS)
        if mode == "cover":
            return ImageOps.fit(source, size, Image.Resampling.LANCZOS)
        contained = ImageOps.contain(source, size, Image.Resampling.LANCZOS)
        result = Image.new("RGBA", size)
        result.alpha_composite(contained, ((size[0] - contained.width) // 2, (size[1] - contained.height) // 2))
        return result
