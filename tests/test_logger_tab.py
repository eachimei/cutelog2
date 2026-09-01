import pytest
from qtpy.QtWidgets import QAbstractItemView

from cutelog2.config import ROOT_LOG
from cutelog2.logger_tab import LoggerTab


@pytest.fixture
def logger_tab(qtbot, main_window_stub):
    tab = LoggerTab(None, 'test', None, ROOT_LOG, main_window_stub)
    qtbot.addWidget(tab)
    return tab


def test_constructs_with_ui_and_shortcuts(logger_tab):
    assert logger_tab.loggerTable is not None
    assert logger_tab.searchSC.key().toString() == 'Ctrl+F'
    assert logger_tab.searchSC_F3.key().toString() == 'F3'


def test_records_reach_the_table(logger_tab, make_record):
    logger_tab.on_record(make_record(message='hello', name='a.b'))
    assert logger_tab.record_model.rowCount() == 1
    assert logger_tab.filter_model.rowCount() == 1


def test_namespace_tree_registers_loggers(logger_tab, make_record):
    logger_tab.on_record(make_record(name='a.b.c'))
    assert logger_tab.namespaceTreeView.model().rowCount() == 1


def test_word_wrap_toggles_scroll_mode(logger_tab):
    logger_tab.set_word_wrap(True)
    assert (logger_tab.loggerTable.verticalScrollMode()
            == QAbstractItemView.ScrollMode.ScrollPerPixel)
    logger_tab.set_word_wrap(False)
    assert (logger_tab.loggerTable.verticalScrollMode()
            == QAbstractItemView.ScrollMode.ScrollPerItem)


def test_extra_mode_toggles(logger_tab, make_record):
    logger_tab.on_record(make_record(message='hi', extra_field='value'))
    logger_tab.set_extra_mode(True)
    assert logger_tab.record_model.extra_mode is True
    logger_tab.set_extra_mode(False)
    assert logger_tab.record_model.extra_mode is False


def test_search_finds_a_record(logger_tab, make_record):
    for message in ['nothing', 'needle', 'nothing else']:
        logger_tab.on_record(make_record(message=message))
    logger_tab.searchLine.setText('needle')
    logger_tab.search_down()
    assert logger_tab.loggerTable.currentIndex().row() == 1


def test_search_with_regex_flag(logger_tab, make_record):
    for message in ['alpha', 'beta42']:
        logger_tab.on_record(make_record(message=message))
    logger_tab.set_search_regex(True)
    logger_tab.searchLine.setText(r'beta\d+')
    logger_tab.search_down()
    assert logger_tab.loggerTable.currentIndex().row() == 1


def test_filter_button_round_trip(logger_tab, make_record):
    for message in ['alpha', 'beta']:
        logger_tab.on_record(make_record(message=message))
    logger_tab.searchLine.setText('alpha')
    logger_tab.filter_or_clear()
    assert logger_tab.filter_model.rowCount() == 1
    logger_tab.filter_or_clear()
    assert logger_tab.filter_model.rowCount() == 2


def test_levels_table_gets_populated(logger_tab, make_record):
    logger_tab.on_record(make_record(levelname='WARNING'))
    assert logger_tab.levelsTable.rowCount() >= 1


def test_disable_and_enable_all_levels(logger_tab, make_record):
    logger_tab.on_record(make_record(levelname='INFO'))
    logger_tab.disable_all_levels()
    assert logger_tab.filter_model.rowCount() == 0
    logger_tab.enable_all_levels()
    assert logger_tab.filter_model.rowCount() == 1
