from pathlib import Path

from PIL import Image

from app.data.models import OperationType, TemplateOperation
from app.engine.flexible_registration import FlexibleTemplateService
from app.engine.templates import TemplateRegistry, TemplateValidator


def test_create_flexible_template_without_legacy_regions(tmp_path: Path) -> None:
    source = tmp_path / "master.png"
    Image.new("RGBA", (300, 200)).save(source)
    operations = [TemplateOperation("logo", "Logo", OperationType.IMAGE_REPLACE, 1, 10, 10, 100, 80,
                                    column="Logo File")]
    path = FlexibleTemplateService().create(source, tmp_path / "template", "Logo Collection", operations)
    template = TemplateRegistry.load(path)
    assert template.schema_version == "2.0"
    assert TemplateValidator().validate(template).passed
