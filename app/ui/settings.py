from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QDialog, QFormLayout, QSpinBox


class SettingsDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Settings")
        layout = QFormLayout(self)
        self.default_dpi = QSpinBox()
        self.default_dpi.setRange(72, 1200)
        self.default_dpi.setValue(300)
        self.stop_on_failure = QCheckBox()
        self.run_qa = QCheckBox()
        self.run_qa.setChecked(True)
        layout.addRow("Default DPI", self.default_dpi)
        layout.addRow("Stop on first failure", self.stop_on_failure)
        layout.addRow("Run QA before export", self.run_qa)

