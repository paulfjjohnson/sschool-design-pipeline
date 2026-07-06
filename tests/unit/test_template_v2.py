from pathlib import Path

import yaml

from app.data.models import OperationType
from app.engine.templates import TemplateRegistry, TemplateValidator


def test_v2_template_loads_arbitrary_ordered_operations(tmp_path: Path) -> None:
    (tmp_path / "master.png").write_bytes(Path("sample_project/template/master.png").read_bytes())
    metadata = {
        "schema_version": "2.0", "template_id": "flex", "name": "Flexible", "version": "1.0",
        "format": "PNG", "source_path": "master.png", "output_width": 240, "output_height": 160,
        "operations": [
            {"operation_id": "logo", "name": "Logo", "operation_type": "IMAGE_REPLACE", "layer_order": 20,
             "x": 10, "y": 10, "width": 50, "height": 50, "column": "Logo File", "config": {"fit": "contain"}},
            {"operation_id": "name", "name": "Name", "operation_type": "TEXT", "layer_order": 10,
             "x": 10, "y": 70, "width": 200, "height": 40, "column": "Display Name"},
        ],
    }
    path = tmp_path / "template.yaml"
    path.write_text(yaml.safe_dump(metadata), encoding="utf-8")

    template = TemplateRegistry.load(path)

    assert [op.operation_id for op in template.operations] == ["name", "logo"]
    assert template.operations[1].operation_type is OperationType.IMAGE_REPLACE
    assert TemplateValidator().validate(template).passed


def test_v1_template_migrates_to_operations() -> None:
    template = TemplateRegistry.load(Path("sample_project/template/template.yaml"))
    assert template.operations
    assert {op.operation_type for op in template.operations} >= {OperationType.TEXT, OperationType.SOLID_COLOR}
