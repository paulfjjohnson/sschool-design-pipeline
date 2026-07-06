from __future__ import annotations

from pathlib import Path
import shutil

from PySide6.QtCore import QThread, Qt, Signal
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
from app.data.models import SchoolStatus
from app.engine.templates import TemplateValidator
from app.ui.models import SchoolQueueModel
from app.ui.preview import PreviewWidget
from app.ui.registration import TemplateRegistrationDialog
from app.ui.settings import SettingsDialog
from app.utils.paths import open_folder


class BatchWorker(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, controller: ApplicationController, *, rebuild_all: bool = False) -> None:
        super().__init__()
        self.controller = controller
        self.rebuild_all = rebuild_all

    def run(self) -> None:
        try:
            operation = self.controller.rebuild_all if self.rebuild_all else self.controller.start_batch
            self.completed.emit(operation())
        except Exception as exc:  # noqa: BLE001 - delivered to the operator on the UI thread.
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self, controller: ApplicationController) -> None:
        super().__init__()
        self.controller = controller
        self.setWindowTitle("School Design Pipeline")
        self.resize(1280, 820)
        self.queue_model = SchoolQueueModel([])
        self.batch_worker: BatchWorker | None = None
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
        self.action_new_project.triggered.connect(self.new_project)
        self.action_open_project = QAction("Open Project", self)
        self.action_open_project.setObjectName("action_open_project")
        self.action_open_project.triggered.connect(self.open_project)
        self.action_save_project = QAction("Save Project", self)
        self.action_save_project.setObjectName("action_save_project")
        self.action_save_project.triggered.connect(self.save_project)
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
        self.action_register_regions.triggered.connect(self.register_template)
        self.action_validate_template = QAction("Validate Template", self)
        self.action_validate_template.triggered.connect(self.validate_template)
        self.action_view_template_metadata = QAction("View Template Metadata", self)
        self.action_view_template_metadata.triggered.connect(self.view_template_metadata)

        self.action_start_batch = QAction("Start Batch", self)
        self.action_start_batch.setObjectName("action_start_batch")
        self.action_start_batch.triggered.connect(self.start_batch)
        self.action_rebuild_all = QAction("Rebuild All", self)
        self.action_rebuild_all.setObjectName("action_rebuild_all")
        self.action_rebuild_all.triggered.connect(self.rebuild_all)
        self.action_pause = QAction("Pause", self)
        self.action_pause.setObjectName("action_pause")
        self.action_pause.triggered.connect(self.pause_batch)
        self.action_resume = QAction("Resume", self)
        self.action_resume.setObjectName("action_resume")
        self.action_resume.triggered.connect(self.resume_batch)
        self.action_stop = QAction("Stop", self)
        self.action_stop.setObjectName("action_stop")
        self.action_stop.triggered.connect(self.stop_batch)
        self.action_reprocess_failed = QAction("Reprocess Failed", self)
        self.action_reprocess_failed.setObjectName("action_reprocess_failed")
        self.action_reprocess_failed.triggered.connect(self.reprocess_failed)
        self.action_skip_selected = QAction("Skip Selected", self)
        self.action_skip_selected.triggered.connect(self.skip_selected)
        self.action_export_completed_log = QAction("Export Completed Log", self)
        self.action_export_completed_log.triggered.connect(self.export_log)

        self.action_view_failed = QAction("View Failed Items", self)
        self.action_view_failed.triggered.connect(self.view_failed)
        self.action_export_qa = QAction("Export QA Report", self)
        self.action_export_qa.triggered.connect(self.export_qa_report)
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
        ):
            template_menu.addAction(action)

        production_menu = self.menuBar().addMenu("Production")
        for action in (
            self.action_start_batch,
            self.action_rebuild_all,
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
            self.action_rebuild_all,
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
            ("Rebuild All", self.action_rebuild_all),
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

    def _refresh_header(self, status: str = "Idle") -> None:
        project = self.controller.project
        template = self.controller.template
        csv_path = project.csv_path if project else None
        self.project_header.setText(
            f"Project: {project.project_name if project else 'Not loaded'} | "
            f"Template: {template.name if template else 'Not loaded'} | "
            f"CSV: {csv_path.name if csv_path else 'Not loaded'} | "
            f"Output: {project.output_path if project else 'Not set'} | Status: {status}"
        )

    def new_project(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose New Project Folder")
        if not path:
            return
        root = Path(path)
        try:
            self.controller.new_project(root.name, root)
        except OSError as exc:
            QMessageBox.critical(self, "Project Creation Failed", str(exc))
            return
        self._refresh_header("Project ready")
        self.log_view.append(f"Created project: {root}")

    def open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "School Design Project (project.json)")
        if not path:
            return
        try:
            self.controller.open_project(Path(path))
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Open Project Failed", str(exc))
            return
        self._refresh_header("Project ready")
        self.queue_model.set_rows(self.controller.queue)
        if self.controller.template:
            self.preview.load_image(self.controller.template.source_path)
        self.log_view.append(f"Opened project: {path}")

    def save_project(self) -> None:
        if self.controller.project is None:
            QMessageBox.warning(self, "No Project", "Create or open a project first.")
            return
        self.controller.project_manager.save_project(self.controller.project)
        self._refresh_header("Saved")

    def register_template(self) -> None:
        if self.controller.project is None:
            QMessageBox.warning(self, "No Project", "Create or open a project before registering artwork.")
            return
        dialog = TemplateRegistrationDialog(self.controller.project.root_path / "template")
        if dialog.exec() and dialog.metadata_path:
            template = self.controller.load_template(dialog.metadata_path)
            self.controller.project.template_id = template.template_id
            self.controller.project.template_version = template.version
            self.controller.project_manager.save_project(self.controller.project)
            self.preview.load_image(template.source_path)
            self._refresh_header("Template registered")

    def load_template(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Template", "", "Template Metadata (*.yaml *.yml)")
        if path:
            try:
                template = self.controller.load_template(Path(path))
            except (OSError, KeyError, ValueError) as exc:
                QMessageBox.critical(self, "Template Load Failed", str(exc))
                return
            self.preview.load_image(template.source_path)
            self._refresh_header("Template loaded")

    def validate_template(self) -> None:
        if self.controller.template is None:
            QMessageBox.warning(self, "No Template", "Load or register a template first.")
            return
        result = TemplateValidator().validate(self.controller.template)
        message = "Template passed validation." if result.passed else "\n".join(result.failures)
        self.qa_panel.setPlainText(message)
        (QMessageBox.information if result.passed else QMessageBox.critical)(self, "Template Validation", message)

    def view_template_metadata(self) -> None:
        template = self.controller.template
        if template is None:
            QMessageBox.warning(self, "No Template", "Load or register a template first.")
            return
        regions = "\n".join(f"{r.name}: {r.x}, {r.y}, {r.width} x {r.height}" for r in template.editable_regions)
        QMessageBox.information(self, "Template Metadata", f"{template.name} v{template.version}\n{template.output_width} x {template.output_height}\n\n{regions}")

    def load_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                rows = self.controller.load_csv(Path(path))
            except (OSError, ValueError) as exc:
                QMessageBox.critical(self, "CSV Load Failed", str(exc))
                return
            self.queue_model.set_rows(rows)
            self.log_view.append(f"Loaded {len(rows)} schools from {path}")
            self._refresh_header("CSV loaded")

    def start_batch(self) -> None:
        if self.batch_worker and self.batch_worker.isRunning():
            return
        if self.controller.project is None or self.controller.template is None or not self.controller.queue:
            QMessageBox.warning(self, "Batch Not Ready", "Create or open a project, register a template, and load a CSV first.")
            return
        self.batch_worker = BatchWorker(self.controller)
        self.batch_worker.completed.connect(self._batch_completed)
        self.batch_worker.failed.connect(self._batch_failed)
        self.batch_worker.start()
        self._refresh_header("Running")
        self.statusBar().showMessage("Processing")

    def rebuild_all(self) -> None:
        if self.batch_worker and self.batch_worker.isRunning():
            return
        if self.controller.project is None or self.controller.template is None or not self.controller.queue:
            QMessageBox.warning(self, "Batch Not Ready", "Load a project, template, and CSV first.")
            return
        answer = QMessageBox.question(
            self,
            "Rebuild All Schools",
            "Regenerate every valid school and overwrite matching output files?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.batch_worker = BatchWorker(self.controller, rebuild_all=True)
        self.batch_worker.completed.connect(self._batch_completed)
        self.batch_worker.failed.connect(self._batch_failed)
        self.batch_worker.start()
        self._refresh_header("Rebuilding all")
        self.statusBar().showMessage("Rebuilding all schools")

    def _batch_completed(self, result) -> None:  # type: ignore[no-untyped-def]
        self.queue_model.set_rows(self.controller.queue)
        self.log_view.append(
            f"Batch complete: {result.completed} completed, {result.failed} failed, {result.skipped} skipped."
        )
        self._refresh_header("Completed")
        self.statusBar().showMessage("Completed")

    def _batch_failed(self, message: str) -> None:
        QMessageBox.critical(self, "Batch Failed", message)
        self._refresh_header("Failed")
        self.statusBar().showMessage("Failed")

    def pause_batch(self) -> None:
        self.controller.batch_processor.pause()
        self._refresh_header("Paused")

    def resume_batch(self) -> None:
        self.controller.batch_processor.resume()
        self._refresh_header("Running")

    def stop_batch(self) -> None:
        self.controller.batch_processor.stop()
        self._refresh_header("Stopped")

    def reprocess_failed(self) -> None:
        if self.controller.project is None or self.controller.template is None:
            QMessageBox.warning(self, "Batch Not Ready", "Load a project and template first.")
            return
        result = self.controller.batch_processor.reprocess_failed(
            self.controller.project, self.controller.template, self.controller.queue
        )
        self.queue_model.set_rows(self.controller.queue)
        self.log_view.append(f"Reprocessed failures: {result.completed} completed, {result.failed} failed.")

    def skip_selected(self) -> None:
        selected = self.queue_view.selectionModel().selectedRows()
        for index in selected:
            self.controller.queue[index.row()].status = SchoolStatus.SKIPPED
        self.queue_model.set_rows(self.controller.queue)

    def view_failed(self) -> None:
        failed = [row for row in self.controller.queue if row.status in {SchoolStatus.FAILED, SchoolStatus.NEEDS_REVIEW}]
        self.qa_panel.setPlainText("\n".join(f"{row.school_name}: {row.notes or row.status.value}" for row in failed) or "No failed items.")

    def export_log(self) -> None:
        if self.controller.project is None:
            QMessageBox.warning(self, "No Project", "Create or open a project first.")
            return
        source = self.controller.project.root_path / "logs" / "school_design_pipeline.log"
        destination, _ = QFileDialog.getSaveFileName(self, "Export Log", "school_design_pipeline.log", "Log Files (*.log)")
        if destination and source.exists():
            shutil.copy2(source, destination)

    def export_qa_report(self) -> None:
        if self.controller.project is None:
            QMessageBox.warning(self, "No Project", "Create or open a project first.")
            return
        source = self.controller.project.root_path / "reports" / "batch_summary.html"
        if not source.exists():
            QMessageBox.warning(self, "No QA Report", "Run a batch first.")
            return
        destination, _ = QFileDialog.getSaveFileName(self, "Export QA Report", "batch_summary.html", "HTML Files (*.html)")
        if destination:
            shutil.copy2(source, destination)

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

