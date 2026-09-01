import pytest
from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush, QColor, QFont, QIcon

from cutelog2.config import CONFIG, Exc_Indication

ROLES = [
    Qt.ItemDataRole.DisplayRole,
    Qt.ItemDataRole.ToolTipRole,
    Qt.ItemDataRole.SizeHintRole,
    Qt.ItemDataRole.DecorationRole,
    Qt.ItemDataRole.FontRole,
    Qt.ItemDataRole.ForegroundRole,
    Qt.ItemDataRole.BackgroundRole,
]


def test_add_record_grows_the_model(record_model, make_record):
    assert record_model.rowCount() == 0
    record_model.add_record(make_record(message='first'))
    record_model.add_record(make_record(message='second'))
    assert record_model.rowCount() == 2
    assert record_model.get_record(1).message == 'second'


@pytest.mark.parametrize('role', ROLES)
def test_every_data_role_is_reachable(record_model, make_record, role):
    record_model.add_record(make_record(message='hello', levelname='ERROR'))
    index = record_model.index(0, 0)
    record_model.data(index, role)


def test_display_role_returns_message(record_model, make_record, table_header):
    record_model.add_record(make_record(message='the message'))
    message_column = [c.name for c in table_header.visible_columns].index('message')
    index = record_model.index(0, message_column)
    assert record_model.data(index, Qt.ItemDataRole.DisplayRole) == 'the message'


def test_font_and_colour_roles_have_qt_types(record_model, make_record):
    record_model.add_record(make_record(levelname='CRITICAL'))
    index = record_model.index(0, 0)
    assert isinstance(record_model.data(index, Qt.ItemDataRole.FontRole), QFont)
    fg = record_model.data(index, Qt.ItemDataRole.ForegroundRole)
    bg = record_model.data(index, Qt.ItemDataRole.BackgroundRole)
    assert fg is None or isinstance(fg, (QColor, QBrush))
    assert bg is None or isinstance(bg, (QColor, QBrush))


def test_dark_theme_switches_colours(record_model, make_record):
    record_model.add_record(make_record(levelname='INFO'))
    index = record_model.index(0, 0)
    record_model.dark_theme = False
    light = record_model.data(index, Qt.ItemDataRole.ForegroundRole)
    record_model.dark_theme = True
    dark = record_model.data(index, Qt.ItemDataRole.ForegroundRole)
    assert light != dark


def test_exception_shows_decoration_icon(record_model, make_record, table_header, monkeypatch):
    monkeypatch.setitem(CONFIG.options, 'exception_indication', Exc_Indication.MSG_ICON)
    record_model.add_record(make_record(exc_text='Traceback (most recent call last): ...'))
    message_column = [c.name for c in table_header.visible_columns].index('message')
    index = record_model.index(0, message_column)
    assert isinstance(record_model.data(index, Qt.ItemDataRole.DecorationRole), QIcon)


def test_exception_red_background(record_model, make_record, monkeypatch):
    monkeypatch.setitem(CONFIG.options, 'exception_indication', Exc_Indication.RED_BG)
    record_model.add_record(make_record(exc_text='boom'))
    index = record_model.index(0, 0)
    assert record_model.data(index, Qt.ItemDataRole.BackgroundRole) is not None


def test_header_data_uses_column_titles(record_model, table_header):
    title = record_model.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
    assert title == table_header.visible_columns[0].title


def test_trim_respects_max_capacity(record_model, make_record):
    record_model.max_capacity = 3
    for i in range(10):
        record_model.add_record(make_record(message=str(i)))
    record_model.trim_if_needed()
    assert 0 < record_model.rowCount() <= 3
    assert record_model.get_record(record_model.rowCount() - 1).message == '9'


def test_clear_empties_the_model(record_model, make_record):
    record_model.add_record(make_record())
    record_model.clear()
    assert record_model.rowCount() == 0
