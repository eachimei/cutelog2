import sys

import qtpy

if not qtpy.PYQT6 and not qtpy.PYSIDE6:
    if sys.platform == 'linux':
        sys.exit("Error: a compatible Qt library couldn't be imported.\n"
                 "Please install python3-pyqt6 (or just python-pyqt6) from your package manager.")
    else:  # this technically shouldn't ever happen
        sys.exit("Error: a compatible Qt library couldn't be imported.\n"
                 "Please install it by running `pip install pyqt6`")


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
