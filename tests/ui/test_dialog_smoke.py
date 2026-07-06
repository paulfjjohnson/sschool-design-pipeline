from pathlib import Path

from PIL import Image
from PySide6.QtCore import QRect

from app.ui.registration import RegionCanvas, TemplateRegistrationDialog
from app.ui.settings import SettingsDialog


def test_registration_dialog_smoke(qtbot) -> None:
    dialog = TemplateRegistrationDialog()
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Register Editable Regions"


def test_settings_dialog_defaults(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    assert dialog.default_dpi.value() == 300
    assert dialog.run_qa.isChecked() is True


def test_registration_canvas_fits_large_image_and_maps_source_coordinates(qtbot, tmp_path: Path) -> None:
    path = tmp_path / "large.png"
    Image.new("RGBA", (2000, 1000)).save(path)
    canvas = RegionCanvas()
    qtbot.addWidget(canvas)
    canvas.set_image(path, (1000, 600))
    canvas.regions["initials"] = QRect(100, 50, 400, 200)

    selection = canvas.selections()["initials"]

    assert canvas.width() == 1000
    assert (selection.x, selection.y, selection.width, selection.height) == (200, 100, 800, 400)
