from qtpy.QtCore import Qt
from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QMessageBox

from .text_view_dialog import TextViewDialog


def show_info_dialog(parent, title, text):
    show_dialog(parent, title, text, QMessageBox.Icon.Information)


def show_warning_dialog(parent, title, text):
    show_dialog(parent, title, text, QMessageBox.Icon.Warning)


def show_critical_dialog(parent, title, text):
    show_dialog(parent, title, text, QMessageBox.Icon.Critical)


def show_dialog(parent, title, text, icon):
    m = QMessageBox(parent)
    m.setWindowModality(Qt.WindowModality.NonModal)
    m.setText(text)
    m.setWindowTitle(title)
    m.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
    m.setIcon(icon)
    m.show()
    center_widget_on_screen(m)


def show_textview_dialog(parent, title, text, icon=QMessageBox.Icon.Information):
    d = TextViewDialog(parent, text)
    d.setWindowModality(Qt.WindowModality.NonModal)
    d.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
    d.setWindowTitle(title)
    d.open()


def center_widget_on_screen(widget):
    screen = widget.screen() or QGuiApplication.primaryScreen()
    if screen is None:
        return
    rect = widget.frameGeometry()
    rect.moveCenter(screen.availableGeometry().center())
    widget.move(rect.topLeft())
