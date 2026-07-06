from PySide6.QtCore import Qt

from app.data.models import SchoolRecord
from app.ui.models import SchoolQueueModel


def test_queue_model_exposes_required_columns() -> None:
    model = SchoolQueueModel([SchoolRecord.example(row_number=1)])

    assert model.headerData(0, Qt.Orientation.Horizontal) == "Status"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "School"
    assert model.headerData(7, Qt.Orientation.Horizontal) == "QA Result"


def test_queue_model_exposes_school_values() -> None:
    model = SchoolQueueModel([SchoolRecord.example(row_number=1)])

    assert model.data(model.index(0, 2), Qt.ItemDataRole.DisplayRole) == "Example Primary 1"
