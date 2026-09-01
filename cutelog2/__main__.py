import importlib.util
import os
import sys

# qtpy picks PyQt5 when it is importable, even if a Qt6 binding is also installed, so the
# choice has to be made before qtpy is imported. PySide6 is the declared dependency, but
# a PyQt6-only install must keep working -- picking an installed binding here avoids the
# fallback warning qtpy would otherwise print on every launch.
if 'QT_API' not in os.environ:
    for _api, _module in (('pyside6', 'PySide6'), ('pyqt6', 'PyQt6')):
        if importlib.util.find_spec(_module) is not None:
            os.environ['QT_API'] = _api
            break

import qtpy


def _fail_with_message(message):
    """gui_scripts entry points have no console, so a bare sys.exit(str) is invisible.

    This path only runs when Qt's own binding selection is already broken, so don't
    route the error through Qt itself (a mismatched/mixed binding can crash showing
    a QMessageBox instead of raising a catchable Python exception).
    """
    if sys.platform == 'win32':
        import ctypes
        MB_ICONERROR = 0x10
        ctypes.windll.user32.MessageBoxW(0, message, "cutelog2: incompatible Qt binding",
                                         MB_ICONERROR)
    sys.exit(message)


if not qtpy.PYQT6 and not qtpy.PYSIDE6:
    detected = f'{qtpy.API_NAME} {qtpy.QT_VERSION}'
    if sys.platform == 'linux':
        _fail_with_message(
            f"Error: cutelog2 requires PyQt6 or PySide6, but qtpy loaded {detected}.\n"
            "Please install python3-pyside6 (or python3-pyqt6) from your package manager.\n"
            "If another Qt binding is also installed, set the QT_API environment variable "
            "to 'pyside6' or 'pyqt6'.")
    else:  # this technically shouldn't ever happen
        _fail_with_message(
            f"Error: cutelog2 requires PyQt6 or PySide6, but qtpy loaded {detected}.\n"
            "Please install it by running `pip install pyside6`.\n"
            "If another Qt binding is also installed, set the QT_API environment variable "
            "to 'pyside6' or 'pyqt6'.")


def main():
    import signal

    from qtpy.QtGui import QIcon
    from qtpy.QtWidgets import QApplication

    from .config import CONFIG, ROOT_LOG, parse_cmdline
    from .main_window import MainWindow
    from .resources_loader import APP_ICON_PATH, register_search_paths

    if sys.platform == 'win32':
        import ctypes
        # Must differ from upstream cutelog's ID, or Windows groups both apps under
        # one taskbar button and icon when they're installed side by side.
        appid = 'cutelog2.cutelog2'
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
