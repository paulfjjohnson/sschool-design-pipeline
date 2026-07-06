from __future__ import annotations

from dataclasses import dataclass

from app.data.models import ColorDefinition
from app.utils.errors import ErrorCategory, PipelineError


class UnknownColorError(PipelineError):
    def __init__(self, color_name: str) -> None:
        super().__init__(
            f'Color "{color_name}" is not mapped in the color library.',
            category=ErrorCategory.DATA,
            suggested_resolution="Add a color mapping or edit the CSV row.",
        )


@dataclass(slots=True)
class ColorLibrary:
    entries: list[ColorDefinition]

    @classmethod
    def default(cls) -> ColorLibrary:
        return cls.from_entries(
            [
                ColorDefinition("Red", "#C8102E", (200, 16, 46), ["scarlet"]),
                ColorDefinition("Royal Blue", "#0057B8", (0, 87, 184), ["royal", "blue royal"]),
                ColorDefinition("Green", "#00843D", (0, 132, 61), ["kelly green"]),
                ColorDefinition("Yellow", "#FFD100", (255, 209, 0), ["gold", "school bus yellow"]),
                ColorDefinition("Black", "#000000", (0, 0, 0), []),
                ColorDefinition("White", "#FFFFFF", (255, 255, 255), []),
                ColorDefinition("Navy", "#00205B", (0, 32, 91), ["navy blue"]),
                ColorDefinition("Purple", "#582C83", (88, 44, 131), []),
                ColorDefinition("Orange", "#FF8200", (255, 130, 0), []),
                ColorDefinition("Gray", "#8A8D8F", (138, 141, 143), ["grey"]),
                ColorDefinition("Blue", "#0067B1", (0, 103, 177), ["true blue"]),
                ColorDefinition("Maroon", "#800020", (128, 0, 32), ["burgundy", "cardinal"]),
                ColorDefinition("Hunter Green", "#355E3B", (53, 94, 59), ["forest green", "dark green"]),
                ColorDefinition("Teal", "#008080", (0, 128, 128), ["aqua teal"]),
                ColorDefinition("Light Blue", "#6CB4EE", (108, 180, 238), ["sky blue", "carolina blue"]),
                ColorDefinition("Pink", "#E83E8C", (232, 62, 140), ["hot pink"]),
                ColorDefinition("Brown", "#6F4E37", (111, 78, 55), ["chocolate"]),
                ColorDefinition("Vegas Gold", "#C5B358", (197, 179, 88), ["old gold"]),
                ColorDefinition("Silver", "#A7A9AC", (167, 169, 172), ["metallic silver"]),
                ColorDefinition("Lime", "#78BE20", (120, 190, 32), ["lime green"]),
                ColorDefinition("Coral", "#FF6F61", (255, 111, 97), []),
                ColorDefinition("Cream", "#FFFDD0", (255, 253, 208), ["ivory"]),
            ]
        )

    @classmethod
    def from_entries(cls, entries: list[ColorDefinition]) -> ColorLibrary:
        return cls(entries=entries)

    def resolve(self, name: str) -> ColorDefinition:
        key = _normalize(name)
        for entry in self.entries:
            names = [entry.display_name, *entry.aliases]
            if key in {_normalize(candidate) for candidate in names}:
                return entry
        raise UnknownColorError(name)


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("-", " ").split())

