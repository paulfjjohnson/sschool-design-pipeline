from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Mapping, TypeVar, get_args, get_origin, get_type_hints

import yaml

from app.data.models import to_primitive

T = TypeVar("T")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_primitive(value), indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path, model: type[T]) -> T:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _coerce(raw, model)


def read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def write_yaml(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(to_primitive(value), handle, sort_keys=True)


def _coerce(value: Any, annotation: Any) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if annotation is Any:
        return value
    if origin in (list, tuple):
        item_type = args[0] if args else Any
        coerced = [_coerce(item, item_type) for item in value]
        return tuple(coerced) if origin is tuple else coerced
    if origin is type(None):
        return None
    if origin is not None and type(None) in args:
        if value is None:
            return None
        non_none = [arg for arg in args if arg is not type(None)][0]
        return _coerce(value, non_none)
    if annotation is Path:
        return Path(value)
    if hasattr(annotation, "__mro__") and any(base.__name__ == "Enum" for base in annotation.__mro__):
        return annotation(value)
    if is_dataclass(annotation):
        type_hints = get_type_hints(annotation)
        data = {}
        for field in fields(annotation):
            if field.name in value:
                data[field.name] = _coerce(value[field.name], type_hints[field.name])
        return annotation(**data)
    return value
