from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageOps

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
