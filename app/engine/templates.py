from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from pathlib import Path

from PIL import Image

from app.data.models import EditableRegion, RegionType, Template
from app.engine.migration import migrate_v1_regions, parse_v2_operations
from app.data.serialization import read_yaml
from app.utils.errors import ErrorCategory, PipelineError


class TemplateValidationError(PipelineError):
    def __init__(self, message: str) -> None:
        super().__init__(message, category=ErrorCategory.TEMPLATE)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    passed: bool
    failures: list[str]


class TemplateRegistry:
    required_regions = {"initials", "script", "floral", "outline"}

    @classmethod
    def load(cls, metadata_path: Path) -> Template:
        data = read_yaml(metadata_path)
        root = metadata_path.parent
        source_path = (root / data["source_path"]).resolve()
        regions = [
            EditableRegion(
                region_id=str(item["region_id"]),
                name=str(item["name"]),
                region_type=RegionType(str(item["region_type"])),
                x=int(item["x"]),
                y=int(item["y"]),
                width=int(item["width"]),
                height=int(item["height"]),
                rotation=float(item.get("rotation", 0.0)),
                locked=bool(item.get("locked", False)),
                mask_path=(root / item["mask_path"]).resolve() if item.get("mask_path") else None,
                selector=item.get("selector"),
            )
            for item in data.get("editable_regions", [])
        ]
        checksum = _sha256(source_path)
        operations = parse_v2_operations(data.get("operations", []), root) if data.get("operations") else migrate_v1_regions(regions)
        if not regions and operations:
            regions = [EditableRegion(op.operation_id, op.name, RegionType.TEXT if op.operation_type.value == "TEXT" else RegionType.COLOR,
                                      op.x, op.y, op.width, op.height, mask_path=op.mask_path)
                       for op in operations if op.operation_type.value != "LOCKED"]
        return Template(
            template_id=str(data["template_id"]),
            name=str(data["name"]),
            version=str(data["version"]),
            format=str(data["format"]).upper(),
            source_path=source_path,
            editable_regions=regions,
            geometry_checksum=checksum,
            output_width=int(data["output_width"]),
            output_height=int(data["output_height"]),
            default_font=(root / data["default_font"]).resolve() if data.get("default_font") else None,
            script_font=(root / data["script_font"]).resolve() if data.get("script_font") else None,
            script_case=str(data.get("script_case", "as_entered")),
            pattern_path=(root / data["pattern_path"]).resolve() if data.get("pattern_path") else None,
            pattern_treatment=str(data.get("pattern_treatment", "preserve")),
            operations=operations,
            schema_version=str(data.get("schema_version", "1.0")),
        )


class TemplateValidator:
    def validate(self, template: Template) -> ValidationResult:
        failures: list[str] = []
        if template.format not in {"PNG", "SVG"}:
            failures.append(f"Unsupported template format: {template.format}")
        if not template.source_path.exists():
            failures.append(f"Missing template source: {template.source_path}")
        if not template.schema_version.startswith("2"):
            region_names = {region.name for region in template.editable_regions}
            missing = TemplateRegistry.required_regions - region_names
            if missing:
                failures.append(f"Missing editable regions: {', '.join(sorted(missing))}")
        else:
            operation_ids = [operation.operation_id for operation in template.operations]
            if not operation_ids:
                failures.append("Template has no registered operations.")
            if len(operation_ids) != len(set(operation_ids)):
                failures.append("Operation IDs must be unique.")
            for operation in template.operations:
                if operation.width <= 0 or operation.height <= 0:
                    failures.append(f"Operation {operation.name} has invalid dimensions.")
                if operation.x < 0 or operation.y < 0 or operation.x + operation.width > template.output_width or operation.y + operation.height > template.output_height:
                    failures.append(f"Operation {operation.name} is outside the output canvas.")
                if operation.mask_path and not operation.mask_path.exists():
                    failures.append(f"Operation {operation.name} mask is missing: {operation.mask_path}")
        for region in template.editable_regions:
            if region.width <= 0 or region.height <= 0:
                failures.append(f"Region {region.name} has invalid dimensions.")
            if region.mask_path and not region.mask_path.exists():
                failures.append(f"Region {region.name} mask is missing: {region.mask_path}")
        if template.format == "PNG" and template.source_path.exists():
            image = Image.open(template.source_path)
            if image.size != (template.output_width, template.output_height):
                failures.append("Template source dimensions do not match output profile.")
        return ValidationResult(passed=not failures, failures=failures)


def with_geometry_checksum(template: Template) -> Template:
    return replace(template, geometry_checksum=_sha256(template.source_path))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

