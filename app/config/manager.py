from __future__ import annotations

from pathlib import Path
from typing import Any

from app.data.models import AppSettings
from app.data.serialization import read_yaml


class ConfigurationManager:
    def __init__(self, defaults_path: Path = Path("app/config/defaults.yaml")) -> None:
        self.defaults_path = defaults_path

    def load(self, overrides: dict[str, Any] | None = None) -> AppSettings:
        data = read_yaml(self.defaults_path)
        if overrides:
            data.update(overrides)
        data["default_project_folder"] = Path(data.get("default_project_folder", "projects"))
        data["default_output_folder"] = Path(data.get("default_output_folder", "output"))
        settings = AppSettings(**data)
        self._validate(settings)
        return settings

    @staticmethod
    def _validate(settings: AppSettings) -> None:
        if settings.default_dpi <= 0:
            raise ValueError("Default DPI must be positive.")
        if settings.export_format != "PNG":
            raise ValueError("Version 1 exports PNG files only.")
        if settings.maximum_worker_threads < 1:
            raise ValueError("At least one worker thread is required.")
