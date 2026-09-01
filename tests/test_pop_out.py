"""Pop-out / pop-in round trip.

This reparents a live LoggerTab between a QTabWidget and a top-level window and flips
WA_DeleteOnClose. It is the one path where the offscreen platform differs meaningfully
from a real display, and where widget ownership crosses between Qt and Python.
"""

import gc
import weakref

import pytest
from qtpy.QtCore import Qt
from qtpy.QtGui import QAction
from qtpy.QtWidgets import QTabWidget, QWidget

from cutelog2.config import ROOT_LOG
from cutelog2.logger_tab import LoggerTab
from cutelog2.main_window import MainWindow


class MainWindowStub(QWidget):
    """Enough of MainWindow for the pop-out machinery to run against.

    The methods below are the real MainWindow implementations, so a regression in them
    fails here rather than being masked by a reimplementation.
    """

    current_logger_and_index = MainWindow.current_logger_and_index
    pop_out_tab = MainWindow.pop_out_tab
    pop_in_tab = MainWindow.pop_in_tab
    close_popped_out_logger = MainWindow.close_popped_out_logger

    def __init__(self):
        super().__init__()
        self.loggerTabWidget = QTabWidget(self)
        self.loggers_by_name = {}
        self.popped_out_loggers = {}
        self.actionPopIn = QAction('Pop in', self)
        self.log = ROOT_LOG.getChild('stub')

    def add_tab(self, name):
        tab = LoggerTab(None, name, None, ROOT_LOG, self)
        self.loggers_by_name[name] = tab
        self.loggerTabWidget.addTab(tab, name)
        self.loggerTabWidget.setCurrentIndex(self.loggerTabWidget.count() - 1)
        return tab


@pytest.fixture
def window(qtbot):
    stub = MainWindowStub()
    qtbot.addWidget(stub)
    return stub


def test_pop_out_makes_the_tab_a_window(qtbot, window):
    tab = window.add_tab('alpha')
    assert window.loggerTabWidget.count() == 1

    window.pop_out_tab()

    assert window.loggerTabWidget.count() == 0
    assert tab.popped_out is True
    assert bool(tab.windowFlags() & Qt.WindowType.Window)
    assert tab.testAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    assert 'alpha' in window.popped_out_loggers


def test_pop_out_then_pop_in_restores_the_tab(qtbot, window):
    tab = window.add_tab('beta')

    window.pop_out_tab()
    assert window.loggerTabWidget.count() == 0

    window.pop_in_tab(tab)

    assert window.loggerTabWidget.count() == 1
    assert tab.popped_out is False
    assert not tab.testAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    assert window.popped_out_loggers == {}
    assert window.loggerTabWidget.widget(0) is tab


def test_repeated_pop_out_pop_in_is_stable(qtbot, window):
    """The destroyed/closeEvent connection is made on pop-out and dropped on pop-in.

    Getting that pairing wrong raises on the second cycle rather than the first.
    """
    tab = window.add_tab('gamma')
    for _ in range(5):
        window.pop_out_tab()
        window.pop_in_tab(tab)
    assert window.loggerTabWidget.count() == 1
    assert tab.popped_out is False


def test_closing_a_popped_out_tab_releases_it(qtbot, window):
    tab = window.add_tab('delta')
    window.pop_out_tab()
    ref = weakref.ref(tab)

    tab.close()  # WA_DeleteOnClose is set, so this schedules destruction

    assert window.popped_out_loggers == {}, 'close did not deregister the popped-out tab'
    assert window.loggers_by_name == {}

    del tab
    qtbot.wait(50)
    gc.collect()

    assert ref() is None, 'popped-out tab survived being closed'
