from app.ui.registration import TemplateRegistrationDialog
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
