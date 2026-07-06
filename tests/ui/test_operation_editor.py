from app.ui.operation_editor import OperationEditorDialog


def test_operation_editor_adds_and_reorders_operations(qtbot) -> None:
    dialog = OperationEditorDialog(["Name", "Logo File"])
    qtbot.addWidget(dialog)
    dialog.add_operation()
    dialog.add_operation()
    assert dialog.operation_list.count() == 2
    dialog.operation_list.setCurrentRow(1)
    dialog.move_up()
    assert dialog.operation_list.currentRow() == 0
