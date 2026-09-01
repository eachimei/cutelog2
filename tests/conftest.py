import os
import shutil
import tempfile

# Must be set before Qt creates a platform integration.
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from qtpy.QtCore import QSettings

# cutelog2.config builds a QSettings at import time, so the sandbox has to exist before
# any cutelog2 module is imported.
_SETTINGS_DIR = tempfile.mkdtemp(prefix='cutelog2-tests-')
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
for _scope in (QSettings.Scope.UserScope, QSettings.Scope.SystemScope):
    QSettings.setPath(QSettings.Format.IniFormat, _scope, _SETTINGS_DIR)


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_SETTINGS_DIR, ignore_errors=True)


@pytest.fixture(scope='session')
def settings_dir():
    return _SETTINGS_DIR


@pytest.fixture
def make_record():
    """Builds LogRecords the way a SocketHandler client would send them."""
    from cutelog2.logger_tab import LogRecord

    def _make(message='hello', levelname='INFO', name='root', **extra):
        data = {'message': message, 'levelname': levelname, 'name': name}
        data.update(extra)
        return LogRecord(data)

    return _make


@pytest.fixture
def table_header(qtbot):
    from qtpy.QtWidgets import QTableView

    from cutelog2.logger_table_header import LoggerTableHeader

    view = QTableView()
    qtbot.addWidget(view)
    header = LoggerTableHeader(view.horizontalHeader())
    header._view = view  # keep the header view alive for the duration of the test
    return header


@pytest.fixture
def record_model(qtbot, table_header):
    from qtpy.QtWidgets import QWidget

    from cutelog2.log_levels import LevelFilter
    from cutelog2.logger_tab import LogRecordModel

    parent = QWidget()
    qtbot.addWidget(parent)
    level_filter = LevelFilter()
    model = LogRecordModel(parent, level_filter.levels, table_header)
    model.level_filter = level_filter
    return model


@pytest.fixture
def filter_model(qtbot, record_model):
    from cutelog2.logger_tab import LogNamespaceTreeModel, RecordFilter

    proxy = RecordFilter(record_model.parent_widget, LogNamespaceTreeModel(),
                         record_model.level_filter)
    proxy.setSourceModel(record_model)
    return proxy


@pytest.fixture
def main_window_stub(qtbot):
    """Minimal stand-in for MainWindow: a real QObject, but starts no server."""
    from qtpy.QtWidgets import QWidget

    class Stub(QWidget):
        def __init__(self):
            super().__init__()
            self.statuses = []

        def set_status(self, string, timeout=3000):
            self.statuses.append(string)

    stub = Stub()
    qtbot.addWidget(stub)
    return stub
