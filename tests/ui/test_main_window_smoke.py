from PySide6.QtGui import QAction

from app.controller.app_controller import ApplicationController
from app.ui.main_window import MainWindow


def test_main_window_contains_required_actions(qtbot) -> None:
    window = MainWindow(ApplicationController.fake())
    qtbot.addWidget(window)

    assert window.findChild(QAction, "action_start_batch") is not None
    assert window.findChild(QAction, "action_load_template") is not None
    assert window.findChild(QAction, "action_load_csv") is not None
    assert window.findChild(QAction, "action_reprocess_failed") is not None


def test_main_window_contains_required_panels(qtbot) -> None:
    window = MainWindow(ApplicationController.fake())
    qtbot.addWidget(window)

    assert window.queue_view.objectName() == "school_queue"
    assert window.preview.objectName() == "preview"
    assert window.qa_panel.objectName() == "qa_panel"
    assert window.log_view.objectName() == "logs_panel"

