from pathlib import Path

from PIL import Image

from app.engine.registration import RegionSelection, TemplateRegistrationService
from app.engine.templates import TemplateRegistry, TemplateValidator


def test_registration_creates_loadable_template_package(tmp_path: Path) -> None:
    source = tmp_path / "artwork.png"
    Image.new("RGBA", (200, 120), (255, 255, 255, 0)).save(source)
    regions = {
        "initials": RegionSelection(10, 10, 70, 40),
        "script": RegionSelection(20, 70, 150, 30),
        "floral": RegionSelection(90, 10, 50, 40),
        "outline": RegionSelection(5, 5, 145, 50),
    }

    metadata = TemplateRegistrationService().register(
        source_path=source,
        destination=tmp_path / "project" / "template",
        name="Test Artwork",
        regions=regions,
    )

    template = TemplateRegistry.load(metadata)
    assert TemplateValidator().validate(template).passed
    assert template.source_path.name == "master.png"
    assert {region.name for region in template.editable_regions} == set(regions)
    assert all(region.mask_path and region.mask_path.exists() for region in template.editable_regions)


def test_registration_rejects_region_outside_image(tmp_path: Path) -> None:
    source = tmp_path / "artwork.png"
    Image.new("RGBA", (100, 100)).save(source)
    regions = {name: RegionSelection(0, 0, 20, 20) for name in ("initials", "script", "floral", "outline")}
    regions["script"] = RegionSelection(90, 90, 20, 20)

    try:
        TemplateRegistrationService().register(source, tmp_path / "template", "Test", regions)
    except ValueError as exc:
        assert "inside the image" in str(exc)
    else:
        raise AssertionError("Expected invalid region to be rejected")
