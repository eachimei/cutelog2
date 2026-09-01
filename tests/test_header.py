from qtpy.QtCore import Qt

from cutelog2.logger_table_header import ColumnListItem, HeaderEditDialog


def test_check_state_round_trips(qtbot, table_header):
    """Qt6 enums are real enums, so `not check_state` no longer round-trips."""
    dialog = HeaderEditDialog(None, table_header)
    qtbot.addWidget(dialog)

    item = dialog.columnList.item(0)
    assert isinstance(item, ColumnListItem)
    assert item.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked

    item.setData(Qt.ItemDataRole.CheckStateRole, Qt.CheckState.Unchecked)
    assert item.column.visible is False
    assert item.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked

    item.setData(Qt.ItemDataRole.CheckStateRole, Qt.CheckState.Checked)
    assert item.column.visible is True
    assert item.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked


def test_toggle_selected_columns(qtbot, table_header):
    dialog = HeaderEditDialog(None, table_header)
    qtbot.addWidget(dialog)

    item = dialog.columnList.item(0)
    before = item.column.visible
    dialog.columnList.setCurrentItem(item)
    dialog.toggle_selected_columns()
    assert item.column.visible is not before
    dialog.columnList.setCurrentItem(item)  # reset() above cleared the selection
    dialog.toggle_selected_columns()
    assert item.column.visible is before


def test_visible_columns_follow_the_visible_flag(table_header):
    visible = [c for c in table_header.columns if c.visible]
    assert len(table_header.visible_columns) == len(visible)
    visible[0].visible = False
    table_header.regen_visible()
    assert len(table_header.visible_columns) == len(visible) - 1
