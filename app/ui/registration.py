from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout


class TemplateRegistrationDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Register Editable Regions")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select and save initials, script, floral, and outline regions."))

