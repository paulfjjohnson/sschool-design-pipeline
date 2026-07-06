from __future__ import annotations

import re
import shutil
from pathlib import Path

from PIL import Image

from app.data.models import TemplateOperation
from app.data.serialization import write_yaml


class FlexibleTemplateService:
    def create(self, source: Path, destination: Path, name: str,
               operations: list[TemplateOperation]) -> Path:
        if source.suffix.lower() != ".png": raise ValueError("Master artwork must be PNG.")
        if not operations: raise ValueError("Add at least one operation.")
        with Image.open(source) as image: width, height = image.size
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination / "master.png")
        payload = []
        for operation in operations:
            if operation.width <= 0 or operation.height <= 0: raise ValueError(f"{operation.name} has invalid bounds.")
            payload.append({"operation_id": operation.operation_id, "name": operation.name,
                "operation_type": operation.operation_type.value, "layer_order": operation.layer_order,
                "x": operation.x, "y": operation.y, "width": operation.width, "height": operation.height,
                "column": operation.column, "default_value": operation.default_value,
                "allow_override": operation.allow_override, "required": operation.required,
                "config": operation.config})
        path = destination / "template.yaml"
        write_yaml(path, {"schema_version": "2.0", "template_id": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
            "name": name, "version": "1.0", "format": "PNG", "source_path": "master.png",
            "output_width": width, "output_height": height, "operations": payload})
        return path
