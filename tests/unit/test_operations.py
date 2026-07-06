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
