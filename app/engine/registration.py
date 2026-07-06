from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from PIL import Image, ImageDraw

from app.data.serialization import write_yaml


@dataclass(frozen=True, slots=True)
class RegionSelection:
    x: int
    y: int
    width: int
    height: int


class TemplateRegistrationService:
    required_regions = ("initials", "script", "floral", "outline")

    def register(
        self,
        source_path: Path,
        destination: Path,
        name: str,
        regions: Mapping[str, RegionSelection],
    ) -> Path:
        if source_path.suffix.lower() != ".png":
            raise ValueError("Template artwork must be a PNG image.")
        missing = set(self.required_regions) - set(regions)
        if missing:
            raise ValueError(f"Missing editable regions: {', '.join(sorted(missing))}")

        with Image.open(source_path) as source:
            width, height = source.size
            for region_name in self.required_regions:
                region = regions[region_name]
                if (
                    region.x < 0
                    or region.y < 0
                    or region.width <= 0
                    or region.height <= 0
                    or region.x + region.width > width
                    or region.y + region.height > height
                ):
                    raise ValueError(f"Region '{region_name}' must be inside the image.")

        destination.mkdir(parents=True, exist_ok=True)
        masks_dir = destination / "masks"
        masks_dir.mkdir(exist_ok=True)
        master_path = destination / "master.png"
        shutil.copy2(source_path, master_path)

        editable_regions: list[dict[str, object]] = []
        for region_name in self.required_regions:
            region = regions[region_name]
            mask = Image.new("L", (width, height), 0)
            ImageDraw.Draw(mask).rectangle(
                (region.x, region.y, region.x + region.width - 1, region.y + region.height - 1),
                fill=255,
            )
            mask_path = masks_dir / f"{region_name}.png"
            mask.save(mask_path)
            editable_regions.append(
                {
                    "region_id": region_name,
                    "name": region_name,
                    "region_type": "TEXT" if region_name in {"initials", "script"} else "COLOR",
                    "x": region.x,
                    "y": region.y,
                    "width": region.width,
                    "height": region.height,
                    "rotation": 0,
                    "locked": False,
                    "mask_path": f"masks/{region_name}.png",
                }
            )

        metadata_path = destination / "template.yaml"
        template_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "registered-template"
        write_yaml(
            metadata_path,
            {
                "template_id": template_id,
                "name": name.strip() or "Registered Template",
                "version": "1.0",
                "format": "PNG",
                "source_path": "master.png",
                "output_width": width,
                "output_height": height,
                "editable_regions": editable_regions,
            },
        )
        return metadata_path
