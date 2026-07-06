from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QPushButton, QScrollArea, QVBoxLayout)

from app.engine.registration import RegionSelection, TemplateRegistrationService


class RegionCanvas(QLabel):
    colors = {"initials": QColor("#22c55e"), "script": QColor("#38bdf8"),
              "floral": QColor("#f472b6"), "outline": QColor("#facc15")}

    def __init__(self) -> None:
        super().__init__("Choose a PNG template image")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.active_region = "initials"
        self.regions: dict[str, QRect] = {}
        self._start: QPoint | None = None
        self._current: QPoint | None = None

    def set_image(self, path: Path) -> None:
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            raise ValueError("The selected PNG could not be opened.")
        self.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())
        self.regions.clear()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.pixmap() and event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._current = self._start

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._start is not None:
            self._current = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._start is None:
            return
        self._current = event.position().toPoint()
        rect = QRect(self._start, self._current).normalized().intersected(self.rect())
        if rect.width() > 1 and rect.height() > 1:
            self.regions[self.active_region] = rect
        self._start = self._current = None
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().paintEvent(event)
        painter = QPainter(self)
        for name, rect in self.regions.items():
            color = self.colors[name]
            painter.setPen(QPen(color, 3))
            painter.drawRect(rect)
            painter.fillRect(rect, QColor(color.red(), color.green(), color.blue(), 35))
            painter.drawText(rect.adjusted(4, 4, -4, -4), Qt.AlignmentFlag.AlignTop, name.title())
        if self._start is not None and self._current is not None:
            painter.setPen(QPen(self.colors[self.active_region], 2, Qt.PenStyle.DashLine))
            painter.drawRect(QRect(self._start, self._current).normalized())

    def selections(self) -> dict[str, RegionSelection]:
        return {name: RegionSelection(rect.x(), rect.y(), rect.width(), rect.height())
                for name, rect in self.regions.items()}


class TemplateRegistrationDialog(QDialog):
    def __init__(self, destination: Path | None = None) -> None:
        super().__init__()
        self.destination = destination
        self.source_path: Path | None = None
        self.metadata_path: Path | None = None
        self.setWindowTitle("Register Editable Regions")
        self.resize(1000, 760)
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        choose = QPushButton("Choose PNG")
        choose.clicked.connect(self.choose_image)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Template name")
        self.region_combo = QComboBox()
        self.region_combo.addItems(list(TemplateRegistrationService.required_regions))
        self.region_combo.currentTextChanged.connect(self._select_region)
        top.addWidget(choose)
        top.addWidget(self.name_edit, 1)
        top.addWidget(QLabel("Draw region:"))
        top.addWidget(self.region_combo)
        layout.addLayout(top)
        self.canvas = RegionCanvas()
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        layout.addWidget(scroll, 1)
        layout.addWidget(QLabel("Choose each region name, then drag a rectangle over that editable area."))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_registration)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _select_region(self, name: str) -> None:
        self.canvas.active_region = name

    def choose_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose Template Artwork", "", "PNG Images (*.png)")
        if path:
            try:
                self.source_path = Path(path)
                self.canvas.set_image(self.source_path)
                self.name_edit.setText(self.source_path.stem.replace("_", " ").title())
            except ValueError as exc:
                QMessageBox.critical(self, "Invalid Image", str(exc))

    def save_registration(self) -> None:
        if self.source_path is None or self.destination is None:
            QMessageBox.warning(self, "Registration Incomplete", "Create a project and choose a PNG image first.")
            return
        missing = set(TemplateRegistrationService.required_regions) - set(self.canvas.regions)
        if missing:
            QMessageBox.warning(self, "Registration Incomplete", f"Draw these regions: {', '.join(sorted(missing))}.")
            return
        try:
            self.metadata_path = TemplateRegistrationService().register(
                self.source_path, self.destination, self.name_edit.text(), self.canvas.selections())
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Registration Failed", str(exc))
            return
        self.accept()
