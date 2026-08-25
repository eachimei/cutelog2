import os
import sys

# qtpy defaults to PyQt5 first if it happens to be importable, even when PyQt6
# is also installed. Steer it to a binding cutelog actually supports, unless
# the environment has already made an explicit choice via QT_API.
os.environ.setdefault('QT_API', 'pyqt6')

import qtpy


def _fail_with_message(message):
    """gui_scripts entry points have no console, so a bare sys.exit(str) is invisible."""
    try:
        from qtpy.QtWidgets import QApplication, QMessageBox
        if QApplication.instance() is None:
            QApplication(sys.argv)
        QMessageBox.critical(None, "cutelog: incompatible Qt binding", message)
    except Exception:
        pass  # whatever got imported can't even show a dialog; fall through to sys.exit
    sys.exit(message)


if not qtpy.PYQT6 and not qtpy.PYSIDE6:
    detected = f'{qtpy.API_NAME} {qtpy.QT_VERSION}'
    if sys.platform == 'linux':
        _fail_with_message(
            f"Error: cutelog requires PyQt6 or PySide6, but qtpy loaded {detected}.\n"
            "Please install python3-pyqt6 (or just python-pyqt6) from your package manager.\n"
            "If another Qt binding is also installed, set the QT_API environment variable "
            "to 'pyqt6' or 'pyside6'.")
    else:  # this technically shouldn't ever happen
        _fail_with_message(
            f"Error: cutelog requires PyQt6 or PySide6, but qtpy loaded {detected}.\n"
            "Please install it by running `pip install pyqt6`.\n"
            "If another Qt binding is also installed, set the QT_API environment variable "
            "to 'pyqt6' or 'pyside6'.")


def main():
    import signal

    from qtpy.QtGui import QIcon
    from qtpy.QtWidgets import QApplication

    from .config import CONFIG, ROOT_LOG, parse_cmdline
    from .main_window import MainWindow
    from .resources_loader import APP_ICON_PATH, register_search_paths

    if sys.platform == 'win32':
        import ctypes
        appid = 'busimus.cutelog'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    app = QApplication(sys.argv)
    register_search_paths()
    app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    overrides, load_logfiles = parse_cmdline(ROOT_LOG)
    CONFIG.set_overrides(overrides)
    mw = MainWindow(ROOT_LOG, app, load_logfiles)
    signal.signal(signal.SIGINT, mw.signal_handler)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
