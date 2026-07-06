from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QScrollArea


class PreviewWidget(QScrollArea):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("preview")
        self.label = QLabel("No preview loaded")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumSize(360, 360)
        self.setWidget(self.label)
        self.setWidgetResizable(True)

    def load_image(self, path: Path) -> None:
        pixmap = QPixmap(str(path))
        self.label.setPixmap(pixmap)

