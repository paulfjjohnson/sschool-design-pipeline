from __future__ import annotations

from pathlib import Path
from typing import Any

from app.data.models import EditableRegion, OperationType, TemplateOperation


def migrate_v1_regions(regions: list[EditableRegion]) -> list[TemplateOperation]:
    mapping = {
        "initials": (OperationType.TEXT, "Generated Initials", 10),
        "floral": (OperationType.PATTERN_FILL, "Pattern File", 20),
        "outline": (OperationType.SOLID_COLOR, "Color 1", 30),
        "script": (OperationType.TEXT, "School", 40),
    }
    operations: list[TemplateOperation] = []
    for region in regions:
        operation_type, column, order = mapping.get(
            region.name, (OperationType.LOCKED, None, 100)
        )
        operations.append(
            TemplateOperation(
                operation_id=region.region_id,
                name=region.name.title(),
                operation_type=operation_type,
                layer_order=order,
                x=region.x,
                y=region.y,
                width=region.width,
                height=region.height,
                column=column,
                mask_path=region.mask_path,
                config={"legacy": True},
            )
        )
    return sorted(operations, key=lambda item: item.layer_order)


def parse_v2_operations(items: list[dict[str, Any]], root: Path) -> list[TemplateOperation]:
    operations = []
    for item in items:
        operations.append(
            TemplateOperation(
                operation_id=str(item["operation_id"]),
                name=str(item["name"]),
                operation_type=OperationType(str(item["operation_type"])),
                layer_order=int(item.get("layer_order", 0)),
                x=int(item["x"]), y=int(item["y"]),
                width=int(item["width"]), height=int(item["height"]),
                column=item.get("column"), default_value=item.get("default_value"),
                allow_override=bool(item.get("allow_override", True)),
                required=bool(item.get("required", False)),
                mask_path=(root / item["mask_path"]).resolve() if item.get("mask_path") else None,
                config=dict(item.get("config", {})),
            )
        )
    return sorted(operations, key=lambda item: item.layer_order)
