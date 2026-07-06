from __future__ import annotations

from dataclasses import dataclass

from app.plugins.api import PluginManifest


@dataclass(frozen=True, slots=True)
class PluginLoadResult:
    accepted: bool
    manifest: PluginManifest | None = None
    reason: str = ""


class PluginManager:
    def __init__(self, engine_version: str) -> None:
        self.engine_version = engine_version
        self.plugins: list[PluginManifest] = []

    def load_manifest(self, data: dict[str, object]) -> PluginLoadResult:
        manifest = PluginManifest(
            name=str(data["name"]),
            version=str(data["version"]),
            author=str(data["author"]),
            minimum_engine_version=str(data["minimum_engine_version"]),
            capabilities=[str(item) for item in data.get("capabilities", [])],
        )
        if _version_tuple(manifest.minimum_engine_version) > _version_tuple(self.engine_version):
            return PluginLoadResult(
                accepted=False,
                manifest=manifest,
                reason=f"{manifest.name} requires engine {manifest.minimum_engine_version}.",
            )
        self.plugins.append(manifest)
        return PluginLoadResult(accepted=True, manifest=manifest)


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))
