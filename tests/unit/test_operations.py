from pathlib import Path

from PIL import Image

from app.data.models import OperationType, TemplateOperation
from app.engine.operations import OperationRenderer
from app.engine.templates import TemplateRegistry


def test_image_replace_uses_mapped_relative_asset(sample_template_path: Path, tmp_path: Path) -> None:
    template = TemplateRegistry.load(sample_template_path)
    logo = tmp_path / "assets" / "logo.png"
    logo.parent.mkdir()
    Image.new("RGBA", (30, 20), (255, 0, 0, 255)).save(logo)
    template.operations = [TemplateOperation(
        "logo", "Logo", OperationType.IMAGE_REPLACE, 1, 10, 10, 60, 40,
        column="Logo File", config={"fit": "contain"},
    )]

    image = OperationRenderer().render(template, {"Logo File": "assets/logo.png"}, tmp_path / "rows.csv")

    assert image.getpixel((40, 30))[0] == 255


def test_visibility_false_clears_only_registered_region(sample_template_path: Path) -> None:
    template = TemplateRegistry.load(sample_template_path)
    template.operations = [TemplateOperation(
        "hide", "Hide", OperationType.VISIBILITY, 1, 20, 20, 30, 30, column="Show",
    )]
    image = OperationRenderer().render(template, {"Show": "no"}, Path("rows.csv"))
    assert image.getpixel((25, 25))[3] == 0
    assert image.getpixel((5, 5))[3] == Image.open(template.source_path).convert("RGBA").getpixel((5, 5))[3]


def test_pattern_text_renders_mapped_text_with_pattern_and_outline(sample_template_path: Path, tmp_path: Path) -> None:
    template = TemplateRegistry.load(sample_template_path)
    pattern = tmp_path / "seersucker.png"
    pattern_image = Image.new("RGBA", (8, 8), (255, 255, 255, 255))
    for x in range(0, 8, 4):
        for stripe_x in (x, x + 1):
            for y in range(8):
                pattern_image.putpixel((stripe_x, y), (0, 0, 255, 255))
    pattern_image.save(pattern)
    template.pattern_path = pattern
    template.operations = [TemplateOperation(
        "mascot",
        "Mascot Pattern Text",
        OperationType.PATTERN_TEXT,
        1,
        0,
        0,
        200,
        80,
        column="Mascot",
        config={
            "case": "upper",
            "outline_color_column": "Color 1",
            "pattern_color_column": "Color 2",
            "outline_width": 4,
            "pattern_treatment": "tint_nonwhite",
        },
    )]

    image = OperationRenderer().render(
        template,
        {"Mascot": "Griffins", "Color 1": "Gray", "Color 2": "Purple"},
        tmp_path / "rows.csv",
    )

    pixels = [image.getpixel((x, y)) for x in range(200) for y in range(80)]
    assert any(pixel[:3] == (138, 141, 143) and pixel[3] == 255 for pixel in pixels)
    assert any(pixel[:3] == (88, 44, 131) and pixel[3] == 255 for pixel in pixels)
    assert image.getbbox() is not None


def test_pattern_text_preserves_letter_counters(sample_template_path: Path, tmp_path: Path) -> None:
    template = TemplateRegistry.load(sample_template_path)
    pattern = tmp_path / "pattern.png"
    Image.new("RGBA", (6, 6), (75, 0, 130, 255)).save(pattern)
    template.pattern_path = pattern
    template.operations = [TemplateOperation(
        "mascot",
        "Mascot Pattern Text",
        OperationType.PATTERN_TEXT,
        1,
        0,
        0,
        120,
        90,
        column="Mascot",
        config={"case": "upper", "outline_color": "Gray", "outline_width": 3},
    )]

    image = OperationRenderer().render(template, {"Mascot": "POP"}, tmp_path / "rows.csv")

    center_alpha_values = [
        image.getpixel((x, y))[3]
        for x in range(45, 75)
        for y in range(22, 55)
    ]
    assert any(alpha == 0 for alpha in center_alpha_values)


def test_pattern_text_tint_saturated_preserves_light_fabric_base(sample_template_path: Path, tmp_path: Path) -> None:
    template = TemplateRegistry.load(sample_template_path)
    pattern = tmp_path / "seersucker.png"
    pattern_image = Image.new("RGBA", (8, 8), (246, 244, 238, 255))
    for x in (1, 2):
        for y in range(8):
            pattern_image.putpixel((x, y), (95, 60, 180, 255))
    pattern_image.save(pattern)
    template.pattern_path = pattern
    template.operations = [TemplateOperation(
        "mascot",
        "Mascot Pattern Text",
        OperationType.PATTERN_TEXT,
        1,
        0,
        0,
        120,
        90,
        column="Mascot",
        config={
            "case": "upper",
            "outline_color": "Gray",
            "pattern_color_column": "Color 2",
            "pattern_treatment": "tint_saturated",
        },
    )]

    image = OperationRenderer().render(template, {"Mascot": "CUBS", "Color 2": "Blue"}, tmp_path / "rows.csv")
    pixels = [image.getpixel((x, y)) for x in range(120) for y in range(90)]

    assert any(pixel[:3] == (246, 244, 238) and pixel[3] == 255 for pixel in pixels)
    assert any(pixel[:3] == (0, 103, 177) and pixel[3] == 255 for pixel in pixels)


def test_pattern_text_can_scale_pattern_tile(tmp_path: Path) -> None:
    source = Image.new("RGBA", (40, 20), (255, 255, 255, 255))
    for x in range(20):
        for y in range(20):
            source.putpixel((x, y), (0, 0, 255, 255))

    scaled = OperationRenderer._scale_pattern(source, 0.5)

    assert scaled.size == (20, 10)


def test_pattern_text_uses_scaled_pattern_tile(sample_template_path: Path, tmp_path: Path) -> None:
    template = TemplateRegistry.load(sample_template_path)
    pattern = tmp_path / "large_stripe.png"
    pattern_image = Image.new("RGBA", (40, 40), (255, 255, 255, 255))
    for x in range(20):
        for y in range(40):
            pattern_image.putpixel((x, y), (0, 0, 255, 255))
    pattern_image.save(pattern)
    template.pattern_path = pattern
    template.operations = [TemplateOperation(
        "mascot",
        "Mascot Pattern Text",
        OperationType.PATTERN_TEXT,
        1,
        0,
        0,
        180,
        90,
        column="Mascot",
        config={"case": "upper", "outline_color": "Gray", "pattern_scale": 0.5},
    )]

    image = OperationRenderer().render(template, {"Mascot": "CUBS"}, tmp_path / "rows.csv")
    row_pixels = [image.getpixel((x, 45))[:3] for x in range(180)]
    transitions = sum(1 for left, right in zip(row_pixels, row_pixels[1:]) if left != right)

    assert transitions >= 4
