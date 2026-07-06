from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from app.data.models import SchoolRecord


class SchoolQueueModel(QAbstractTableModel):
    headers = [
        "Status",
        "Row #",
        "School",
        "Initials",
        "Color 1",
        "Color 2",
        "Output File",
        "QA Result",
    ]

    def __init__(self, rows: list[SchoolRecord] | None = None) -> None:
        super().__init__()
        self.rows = rows or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        record = self.rows[index.row()]
        values = [
            record.status.value,
            record.row_number,
            record.school_name,
            record.initials,
            record.color_primary,
            record.color_secondary,
            record.export_filename,
            record.qa_status.value,
        ]
        return values[index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    def set_rows(self, rows: list[SchoolRecord]) -> None:
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

