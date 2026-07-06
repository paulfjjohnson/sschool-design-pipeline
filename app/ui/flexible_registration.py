from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QDialog, QFileDialog, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.engine.flexible_registration import FlexibleTemplateService
from app.engine.tabular_importer import TabularImporter
from app.ui.operation_editor import OperationEditorDialog


class FlexibleRegistrationDialog(QDialog):
    def __init__(self, destination: Path) -> None:
        super().__init__(); self.destination = destination; self.source: Path | None = None
        self.batch: Path | None = None; self._operations = []; self.metadata_path: Path | None = None
        self.setWindowTitle("Create Flexible Template"); self.resize(620, 220)
        layout = QVBoxLayout(self); self.name = QLineEdit(); self.name.setPlaceholderText("Template name")
        layout.addWidget(self.name)
        row = QHBoxLayout()
        for text, slot in (("Choose Master PNG", self.choose_master), ("Choose CSV/XLSX", self.choose_batch),
                           ("Edit Operations", self.edit_operations)):
            button = QPushButton(text); button.clicked.connect(slot); row.addWidget(button)
        layout.addLayout(row)
        save = QPushButton("Create Template"); save.clicked.connect(self.save); layout.addWidget(save)

    def choose_master(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Master Artwork", "", "PNG Images (*.png)")
        if path: self.source = Path(path); self.name.setText(self.source.stem.replace("_", " ").title())

    def choose_batch(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Sample Batch", "", "Batch Files (*.csv *.xlsx)")
        if path: self.batch = Path(path)

    def edit_operations(self) -> None:
        columns = TabularImporter().import_file(self.batch).columns if self.batch else []
        dialog = OperationEditorDialog(columns, self._operations)
        if dialog.exec(): self._operations = dialog.operations()

    def save(self) -> None:
        if not self.source:
            QMessageBox.warning(self, "Missing Master", "Choose a master PNG first."); return
        try: self.metadata_path = FlexibleTemplateService().create(self.source, self.destination,
            self.name.text().strip() or self.source.stem, self._operations)
        except ValueError as exc: QMessageBox.critical(self, "Template Error", str(exc)); return
        self.accept()
