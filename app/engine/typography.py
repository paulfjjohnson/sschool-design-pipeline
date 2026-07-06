from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.utils.errors import ErrorCategory, PipelineError


class MissingFontError(PipelineError):
    def __init__(self) -> None:
        super().__init__(
            "Required font is missing and default font substitution is not allowed.",
            category=ErrorCategory.TYPOGRAPHY,
            suggested_resolution="Register the required font in the template or project font library.",
        )


class TextRenderer:
    def __init__(self, font_path: Path | None, allow_default_font: bool = False) -> None:
        self.font_path = font_path
        self.allow_default_font = allow_default_font

    @property
    def font_available(self) -> bool:
        return self.font_path is not None and self.font_path.exists()

    def render_text(
        self,
        text: str,
        size: tuple[int, int],
        *,
        fill: tuple[int, int, int, int],
    ) -> Image.Image:
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        font = self._load_font(size)
        draw = ImageDraw.Draw(image)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = max(0, (size[0] - text_width) // 2)
        y = max(0, (size[1] - text_height) // 2 - bbox[1])
        draw.text((x, y), text, font=font, fill=fill)
        return image

    def _load_font(self, size: tuple[int, int]) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
        font_size = max(10, min(size[0] // 3, size[1] - 4))
        if self.font_available:
            return ImageFont.truetype(str(self.font_path), font_size)
        if not self.allow_default_font:
            raise MissingFontError()
        return ImageFont.load_default(font_size)

