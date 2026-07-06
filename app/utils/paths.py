from __future__ import annotations

import os
import re
from pathlib import Path


WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(stem: str, suffix: str = ".png") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._ ")
    if not cleaned:
        cleaned = "untitled"
    if cleaned.upper() in WINDOWS_RESERVED_NAMES:
        cleaned = f"{cleaned}_file"
    return f"{cleaned}{suffix}"


def open_folder(path: Path) -> None:
    os.startfile(path)  # type: ignore[attr-defined]

