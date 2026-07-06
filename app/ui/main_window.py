from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTableView,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.controller.app_controller import ApplicationController
from app.ui.models import SchoolQueueModel
from app.ui.preview import PreviewWidget
from app.ui.registration import TemplateRegistrationDialog
from app.ui.settings import SettingsDialog
from app.utils.paths import open_folder


class MainWindow(QMainWindow):
    def __init__(self, controller: ApplicationController) -> None:
        super().__init__()
        self.controller = controller
        self.setWindowTitle("School Design Pipeline")
        self.resize(1280, 820)
        self.queue_model = SchoolQueueModel([])
        self._build_actions()
        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self._apply_style()
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Idle")

    def _build_actions(self) -> None:
        self.action_new_project = QAction("New Project", self)
        self.action_new_project.setObjectName("action_new_project")
        self.action_open_project = QAction("Open Project", self)
        self.action_open_project.setObjectName("action_open_project")
        self.action_save_project = QAction("Save Project", self)
        self.action_save_project.setObjectName("action_save_project")
        self.action_load_template = QAction("Load Template", self)
        self.action_load_template.setObjectName("action_load_template")
        self.action_load_template.triggered.connect(self.load_template)
        self.action_load_csv = QAction("Load CSV", self)
        self.action_load_csv.setObjectName("action_load_csv")
        self.action_load_csv.triggered.connect(self.load_csv)
        self.action_open_output = QAction("Open Output Folder", self)
        self.action_open_output.setObjectName("action_open_output")
        self.action_open_output.triggered.connect(self.open_output_folder)
        self.action_exit = QAction("Exit", self)
        self.action_exit.triggered.connect(self.close)

        self.action_register_regions = QAction("Register Editable Regions", self)
        self.action_register_regions.triggered.connect(lambda: TemplateRegistrationDialog().exec())
        self.action_validate_template = QAction("Validate Template", self)
        self.action_view_template_metadata = QAction("View Template Metadata", self)
        self.action_duplicate_template = QAction("Duplicate Template", self)
        self.action_lock_template = QAction("Lock Template", self)

        self.action_start_batch = QAction("Start Batch", self)
        self.action_start_batch.setObjectName("action_start_batch")
        self.action_start_batch.triggered.connect(self.start_batch)
        self.action_pause = QAction("Pause", self)
        self.action_pause.setObjectName("action_pause")
        self.action_resume = QAction("Resume", self)
        self.action_resume.setObjectName("action_resume")
        self.action_stop = QAction("Stop", self)
        self.action_stop.setObjectName("action_stop")
        self.action_reprocess_failed = QAction("Reprocess Failed", self)
        self.action_reprocess_failed.setObjectName("action_reprocess_failed")
        self.action_skip_selected = QAction("Skip Selected", self)
        self.action_export_completed_log = QAction("Export Completed Log", self)

        self.action_run_qa_current = QAction("Run QA on Current", self)
        self.action_run_qa_all = QAction("Run QA on All Completed", self)
        self.action_view_failed = QAction("View Failed Items", self)
        self.action_export_qa = QAction("Export QA Report", self)
        self.action_settings = QAction("Settings", self)
        self.action_settings.triggered.connect(lambda: SettingsDialog().exec())

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        for action in (
            self.action_new_project,
            self.action_open_project,
            self.action_save_project,
            self.action_load_template,
            self.action_load_csv,
            self.action_open_output,
            self.action_exit,
        ):
            file_menu.addAction(action)

        template_menu = self.menuBar().addMenu("Template")
        for action in (
            self.action_register_regions,
            self.action_validate_template,
            self.action_view_template_metadata,
            self.action_duplicate_template,
            self.action_lock_template,
        ):
            template_menu.addAction(action)

        production_menu = self.menuBar().addMenu("Production")
        for action in (
            self.action_start_batch,
            self.action_pause,
            self.action_resume,
            self.action_stop,
            self.action_reprocess_failed,
            self.action_skip_selected,
            self.action_export_completed_log,
        ):
            production_menu.addAction(action)

        qa_menu = self.menuBar().addMenu("QA")
        for action in (
            self.action_run_qa_current,
            self.action_run_qa_all,
            self.action_view_failed,
            self.action_export_qa,
        ):
            qa_menu.addAction(action)

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(self.action_settings)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Batch Controls")
        toolbar.setMovable(False)
        for action in (
            self.action_load_template,
            self.action_load_csv,
            self.action_start_batch,
            self.action_pause,
            self.action_resume,
            self.action_stop,
            self.action_reprocess_failed,
            self.action_open_output,
        ):
            toolbar.addAction(action)
        self.addToolBar(toolbar)

    def _build_body(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        self.project_header = QLabel(
            "Project: Not loaded | Template: Not loaded | CSV: Not loaded | Output: Not set | Status: Idle"
        )
        self.project_header.setObjectName("project_header")
        layout.addWidget(self.project_header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.queue_view = QTableView()
        self.queue_view.setObjectName("school_queue")
        self.queue_view.setModel(self.queue_model)
        self.queue_view.setSortingEnabled(True)
        splitter.addWidget(self.queue_view)

        self.preview = PreviewWidget()
        splitter.addWidget(self.preview)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        for label, action in (
            ("Start", self.action_start_batch),
            ("Pause", self.action_pause),
            ("Resume", self.action_resume),
            ("Stop", self.action_stop),
            ("Reprocess Failed", self.action_reprocess_failed),
            ("Open Output", self.action_open_output),
        ):
            button = QPushButton(label)
            button.clicked.connect(action.trigger)
            right_layout.addWidget(button)
        self.qa_panel = QTextEdit()
        self.qa_panel.setObjectName("qa_panel")
        self.qa_panel.setReadOnly(True)
        self.qa_panel.setPlaceholderText("QA results")
        self.log_view = QTextEdit()
        self.log_view.setObjectName("logs_panel")
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Logs")
        right_layout.addWidget(QLabel("QA"))
        right_layout.addWidget(self.qa_panel)
        right_layout.addWidget(QLabel("Logs"))
        right_layout.addWidget(self.log_view)
        splitter.addWidget(right_panel)
        splitter.setSizes([420, 520, 340])
        layout.addWidget(splitter)
        self.setCentralWidget(root)

    def load_template(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Template", "", "Template Metadata (*.yaml *.yml)")
        if path:
            template = self.controller.load_template(Path(path))
            self.project_header.setText(f"Template: {template.name} v{template.version}")
            self.preview.load_image(template.source_path)

    def load_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load CSV", "", "CSV Files (*.csv)")
        if path:
            rows = self.controller.load_csv(Path(path))
            self.queue_model.set_rows(rows)
            self.log_view.append(f"Loaded {len(rows)} schools from {path}")

    def start_batch(self) -> None:
        try:
            result = self.controller.start_batch()
        except Exception as exc:  # noqa: BLE001 - show actionable UI error.
            QMessageBox.critical(self, "Batch Failed", str(exc))
            return
        self.queue_model.set_rows(self.controller.queue)
        self.log_view.append(
            f"Batch complete: {result.completed} completed, {result.failed} failed, {result.skipped} skipped."
        )
        self.statusBar().showMessage("Completed")

    def open_output_folder(self) -> None:
        if self.controller.project and self.controller.project.output_path:
            open_folder(self.controller.project.output_path)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #0f172a; color: #f8fafc; font-family: 'Segoe UI'; }
            QLabel#project_header { padding: 8px; background: #1e293b; border: 1px solid #334155; }
            QTableView, QTextEdit, QScrollArea { background: #111827; color: #f8fafc; border: 1px solid #334155; }
            QPushButton { min-height: 32px; padding: 6px 10px; background: #334155; border: 1px solid #475569; }
            QPushButton:focus, QTableView:focus, QTextEdit:focus { border: 2px solid #22c55e; }
            QToolBar { background: #1e293b; border-bottom: 1px solid #334155; }
            QMenuBar, QMenu { background: #1e293b; color: #f8fafc; }
            """
        )

