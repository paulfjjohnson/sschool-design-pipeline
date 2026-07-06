from pathlib import Path

import yaml

from app.controller.app_controller import ApplicationController


def test_v2_collection_maps_arbitrary_csv_column_and_exports(tmp_path: Path) -> None:
    controller = ApplicationController()
    project = controller.new_project("Flexible", tmp_path)
    master = Path("sample_project/template/master.png")
    (tmp_path / "template" / "master.png").write_bytes(master.read_bytes())
    metadata = {
        "schema_version": "2.0", "template_id": "flex", "name": "Flexible", "version": "1.0",
        "format": "PNG", "source_path": "master.png", "output_width": 240, "output_height": 160,
        "operations": [{"operation_id": "accent", "name": "Accent", "operation_type": "SOLID_COLOR",
            "layer_order": 1, "x": 20, "y": 20, "width": 40, "height": 30, "column": "Accent Color"}],
    }
    metadata_path = tmp_path / "template" / "template.yaml"
    metadata_path.write_text(yaml.safe_dump(metadata), encoding="utf-8")
    csv_path = tmp_path / "input" / "items.csv"
    csv_path.write_text("Name,Accent Color\nAlpha,Teal\n", encoding="utf-8")
    controller.load_template(metadata_path)
    controller.load_csv(csv_path)

    result = controller.start_batch()

    assert result.completed == 1
    assert list(project.output_path.glob("*.png"))
