from pathlib import Path

from app.engine.templates import TemplateRegistry, TemplateValidator


def test_template_requires_all_registered_regions(sample_template_path: Path) -> None:
    template = TemplateRegistry.load(sample_template_path)
    result = TemplateValidator().validate(template)

    assert result.passed
    assert {region.name for region in template.editable_regions} == {
        "initials",
        "script",
        "floral",
        "outline",
    }
    assert template.geometry_checksum

