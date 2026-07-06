from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from PIL import Image, ImageDraw

from app.data.models import SchoolRecord


@pytest.fixture
def sample_school() -> SchoolRecord:
    return SchoolRecord(
        row_number=1,
        school_name="Pecan Grove Primary",
        mascot="Pelicans",
        color_primary="Red",
        color_secondary="Royal",
        initials="PGP",
        export_filename="Pecan_Grove_Primary_FloralVarsity.png",
    )


@pytest.fixture
def sample_template_dir(tmp_path: Path) -> Path:
    template_dir = tmp_path / "template"
    masks_dir = template_dir / "masks"
    masks_dir.mkdir(parents=True)

    master = Image.new("RGBA", (240, 160), (0, 0, 0, 0))
    draw = ImageDraw.Draw(master)
    draw.rectangle((5, 5, 235, 155), outline=(30, 30, 30, 255), width=2)
    draw.rectangle((20, 20, 130, 80), fill=(245, 196, 0, 255))
    draw.rectangle((18, 18, 132, 82), outline=(255, 255, 255, 255), width=4)
    draw.rectangle((30, 92, 210, 125), fill=(80, 80, 80, 255))
    master.save(template_dir / "master.png")

    _save_mask(masks_dir / "initials.png", (240, 160), (20, 20, 130, 80))
    _save_mask(masks_dir / "outline.png", (240, 160), (18, 18, 132, 82))
    _save_mask(masks_dir / "script.png", (240, 160), (30, 92, 210, 125))
    _save_mask(masks_dir / "floral.png", (240, 160), (45, 30, 115, 70))

    metadata = {
        "template_id": "floral-varsity-test",
        "name": "Floral Varsity",
        "version": "1.0",
        "format": "PNG",
        "source_path": "master.png",
        "output_width": 240,
        "output_height": 160,
        "editable_regions": [
            _region("initials", "TEXT", 20, 20, 110, 60, "masks/initials.png"),
            _region("outline", "COLOR", 18, 18, 114, 64, "masks/outline.png"),
            _region("script", "TEXT", 30, 92, 180, 33, "masks/script.png"),
            _region("floral", "COLOR", 45, 30, 70, 40, "masks/floral.png"),
        ],
    }
    (template_dir / "template.yaml").write_text(yaml.safe_dump(metadata), encoding="utf-8")
    return template_dir


@pytest.fixture
def sample_template_path(sample_template_dir: Path) -> Path:
    return sample_template_dir / "template.yaml"


def _save_mask(path: Path, size: tuple[int, int], box: tuple[int, int, int, int]) -> None:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle(box, fill=255)
    mask.save(path)


def _region(
    name: str,
    region_type: str,
    x: int,
    y: int,
    width: int,
    height: int,
    mask_path: str,
) -> dict[str, object]:
    return {
        "region_id": name,
        "name": name,
        "region_type": region_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "rotation": 0,
        "locked": False,
        "mask_path": mask_path,
    }

