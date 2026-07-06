from pathlib import Path

from app.config.manager import ConfigurationManager


def test_configuration_defaults_load() -> None:
    settings = ConfigurationManager(defaults_path=Path("app/config/defaults.yaml")).load()

    assert settings.default_dpi == 300
    assert settings.export_format == "PNG"
    assert settings.transparent_background is True

