from __future__ import annotations

from pathlib import Path


class AssetResolver:
    def resolve(self, value: str, spreadsheet_path: Path) -> Path:
        if not value.strip():
            raise ValueError("Asset path is empty.")
        candidate = Path(value.strip())
        if not candidate.is_absolute():
            candidate = spreadsheet_path.parent / candidate
        candidate = candidate.resolve()
        if not candidate.is_file():
            raise ValueError(f"Asset file does not exist: {candidate}")
        return candidate
