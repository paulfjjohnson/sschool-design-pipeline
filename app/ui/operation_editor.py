from __future__ import annotations

import json

from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QHBoxLayout, QLineEdit, QListWidget, QPushButton, QSpinBox, QVBoxLayout)

from app.data.models import OperationType, TemplateOperation


class OperationEditorDialog(QDialog):
    def __init__(self, columns: list[str], operations: list[TemplateOperation] | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Template Operations")
        self.resize(760, 520)
        self.columns = columns
        self._operations = list(operations or [])
        root = QHBoxLayout(self)
        left = QVBoxLayout()
        self.operation_list = QListWidget()
        self.operation_list.currentRowChanged.connect(self._load)
        left.addWidget(self.operation_list)
        buttons = QHBoxLayout()
        for text, slot in (("Add", self.add_operation), ("Remove", self.remove_operation),
                           ("Up", self.move_up), ("Down", self.move_down)):
            button = QPushButton(text); button.clicked.connect(slot); buttons.addWidget(button)
        left.addLayout(buttons); root.addLayout(left, 1)
        form = QFormLayout()
        self.name = QLineEdit(); self.kind = QComboBox(); self.kind.addItems([item.value for item in OperationType])
        self.column = QComboBox(); self.column.addItem(""); self.column.addItems(columns)
        self.default = QLineEdit(); self.override = QCheckBox(); self.override.setChecked(True)
        self.config = QLineEdit()
        self.config.setPlaceholderText('{"case":"upper","outline_color_column":"Color 1","pattern_color_column":"Color 2","outline_width":8}')
        self.required = QCheckBox()
        self.x, self.y, self.width, self.height = (QSpinBox() for _ in range(4))
        for field in (self.x, self.y, self.width, self.height): field.setRange(0, 100000)
        for label, field in (("Name", self.name), ("Type", self.kind), ("Spreadsheet column", self.column),
                             ("Default", self.default), ("Allow row override", self.override),
                             ("Configuration JSON", self.config), ("Required", self.required), ("X", self.x), ("Y", self.y),
                             ("Width", self.width), ("Height", self.height)):
            form.addRow(label, field)
        save = QPushButton("Apply Changes"); save.clicked.connect(self._store); form.addRow(save)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        dialog_buttons.accepted.connect(self._accept); dialog_buttons.rejected.connect(self.reject); form.addRow(dialog_buttons)
        root.addLayout(form, 2)
        for operation in self._operations: self.operation_list.addItem(operation.name)

    def add_operation(self) -> None:
        index = len(self._operations)
        self._operations.append(TemplateOperation(f"operation-{index + 1}", f"Operation {index + 1}",
                                                  OperationType.TEXT, index * 10, 0, 0, 100, 100))
        self.operation_list.addItem(self._operations[-1].name); self.operation_list.setCurrentRow(index)

    def remove_operation(self) -> None:
        row = self.operation_list.currentRow()
        if row >= 0: self._operations.pop(row); self.operation_list.takeItem(row)

    def move_up(self) -> None: self._move(-1)
    def move_down(self) -> None: self._move(1)

    def _move(self, delta: int) -> None:
        row = self.operation_list.currentRow(); target = row + delta
        if row < 0 or target < 0 or target >= len(self._operations): return
        self._operations[row], self._operations[target] = self._operations[target], self._operations[row]
        item = self.operation_list.takeItem(row); self.operation_list.insertItem(target, item); self.operation_list.setCurrentRow(target)

    def _load(self, row: int) -> None:
        if row < 0 or row >= len(self._operations): return
        op = self._operations[row]; self.name.setText(op.name); self.kind.setCurrentText(op.operation_type.value)
        self.column.setCurrentText(op.column or ""); self.default.setText(op.default_value or "")
        self.override.setChecked(op.allow_override); self.required.setChecked(op.required)
        self.config.setText(json.dumps(op.config, separators=(",", ":")))
        for widget, value in ((self.x, op.x), (self.y, op.y), (self.width, op.width), (self.height, op.height)): widget.setValue(value)

    def _store(self) -> None:
        row = self.operation_list.currentRow()
        if row < 0: return
        old = self._operations[row]
        self._operations[row] = TemplateOperation(old.operation_id, self.name.text().strip() or old.name,
            OperationType(self.kind.currentText()), row * 10, self.x.value(), self.y.value(), self.width.value(),
            self.height.value(), self.column.currentText() or None, self.default.text() or None,
            self.override.isChecked(), self.required.isChecked(), old.mask_path,
            json.loads(self.config.text() or "{}"))
        self.operation_list.item(row).setText(self._operations[row].name)

    def _accept(self) -> None:
        self._store(); self.accept()

    def operations(self) -> list[TemplateOperation]:
        return self._operations
