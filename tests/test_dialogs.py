"""Constructing every dialog is enough to trip most unscoped-enum regressions."""
from types import SimpleNamespace

import pytest
from qtpy.QtWidgets import QDialog

from cutelog2.about_dialog import AboutDialog
from cutelog2.level_edit_dialog import LevelEditDialog
from cutelog2.levels_preset_dialog import LevelsPresetDialog
from cutelog2.log_levels import DEFAULT_LEVELS, LogLevel
from cutelog2.logger_table_header import CreateNewColumnDialog, HeaderEditDialog
from cutelog2.merge_dialog import MergeDialog
from cutelog2.pop_in_dialog import PopInDialog
from cutelog2.settings_dialog import SettingsDialog
from cutelog2.text_view_dialog import TextViewDialog


@pytest.fixture
def parent(qtbot):
    from qtpy.QtWidgets import QWidget

    widget = QWidget()
    qtbot.addWidget(widget)
    return widget


def show(qtbot, dialog):
    qtbot.addWidget(dialog)
    assert isinstance(dialog, QDialog)
    return dialog


def test_about_dialog(qtbot, parent):
    show(qtbot, AboutDialog(parent))


def test_settings_dialog(qtbot, parent):
    dialog = show(qtbot, SettingsDialog(parent))
    assert dialog.applyButton is not None
    assert dialog.restoreDefaultsButton is not None


def test_text_view_dialog(qtbot, parent):
    dialog = show(qtbot, TextViewDialog(parent, 'some text'))
    assert dialog.textEdit.toPlainText() == 'some text'


def test_level_edit_dialog(qtbot, parent):
    level = LogLevel('INFO')
    show(qtbot, LevelEditDialog(parent, level, level_names=['INFO', 'DEBUG']))


def test_level_edit_dialog_for_new_level(qtbot, parent):
    show(qtbot, LevelEditDialog(parent, creating_new_level=True, level_names=['INFO']))


def test_levels_preset_dialog(qtbot, parent):
    show(qtbot, LevelsPresetDialog(parent, 'Stock', dict(DEFAULT_LEVELS)))


def test_merge_dialog(qtbot, parent):
    dialog = show(qtbot, MergeDialog(parent, {'one': None, 'two': None}))
    assert dialog.loggerList.count() == 2


def test_pop_in_dialog(qtbot, parent):
    popped_out = [SimpleNamespace(name=name, popped_out=True) for name in ('one', 'two')]
    docked = [SimpleNamespace(name='three', popped_out=False)]
    dialog = show(qtbot, PopInDialog(parent, popped_out + docked))
    assert dialog.listWidget.count() == 2


def test_header_edit_dialog(qtbot, parent, table_header):
    dialog = show(qtbot, HeaderEditDialog(parent, table_header))
    assert dialog.columnList.count() == len(table_header.columns)


def test_create_new_column_dialog(qtbot, parent):
    show(qtbot, CreateNewColumnDialog(parent))
