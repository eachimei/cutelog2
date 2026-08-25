from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QWidget

from cutelog.utils import center_widget_on_screen


def test_center_widget_on_screen(qtbot):
    """QDesktopWidget is gone in Qt6; centring must work off QScreen instead."""
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.resize(200, 100)
    widget.move(0, 0)

    center_widget_on_screen(widget)

    available = QGuiApplication.primaryScreen().availableGeometry()
    assert widget.frameGeometry().center().x() == available.center().x()
    assert widget.frameGeometry().center().y() == available.center().y()
