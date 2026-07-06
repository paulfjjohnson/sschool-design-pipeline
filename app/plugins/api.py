from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PluginManifest:
    name: str
    version: str
    author: str
    minimum_engine_version: str
    capabilities: list[str]


class TemplateEnginePlugin(Protocol):
    manifest: PluginManifest


class ExporterPlugin(Protocol):
    manifest: PluginManifest


class QAPlugin(Protocol):
    manifest: PluginManifest


class ColorLibraryPlugin(Protocol):
    manifest: PluginManifest


class FontProviderPlugin(Protocol):
    manifest: PluginManifest


class ReportPlugin(Protocol):
    manifest: PluginManifest

