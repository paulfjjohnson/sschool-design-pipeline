import pytest

from app.engine.colors import ColorLibrary, UnknownColorError


def test_color_library_resolves_display_name_and_alias() -> None:
    library = ColorLibrary.default()

    assert library.resolve("Royal").hex == "#0057B8"
    assert library.resolve("royal blue").display_name == "Royal Blue"


def test_unknown_color_raises_actionable_error() -> None:
    library = ColorLibrary.from_entries([])

    with pytest.raises(UnknownColorError, match="Maroon"):
        library.resolve("Maroon")


def test_apparel_palette_resolves_common_school_colors() -> None:
    library = ColorLibrary.default()
    for name in ("Blue", "Maroon", "Hunter Green", "Teal", "Light Blue", "Pink", "Brown", "Vegas Gold"):
        assert library.resolve(name).hex.startswith("#")

