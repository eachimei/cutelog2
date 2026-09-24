"""Loading records from files and standard input, and the view-only launch options."""

import io
import json
import sys

import pytest

from cutelog2.config import CONFIG, OPTION_SPEC, ROOT_LOG, parse_cmdline
from cutelog2.main_window import LoadingThread, MainWindow

NON_ASCII = 'naïve café ✓ 日本'


def run_loader(path, tab_name=None):
    """Run LoadingThread.run() on the calling thread and return (loaded, errors)."""
    lt = LoadingThread(str(path), ROOT_LOG, tab_name=tab_name)
    loaded, errors = [], []
    lt.done_loading.connect(loaded.append)
    lt.loading_error.connect(errors.append)
    lt.run()
    return loaded, errors


def fake_stdin(monkeypatch, data):
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(data), encoding='ascii'))


def records_json(n=1, msg='hello'):
    return [{'name': 'root', 'levelname': 'INFO', 'msg': f'{msg} {i}'} for i in range(n)]


@pytest.mark.parametrize('encoding', ['utf-8', 'utf-8-sig'])
def test_file_is_read_as_utf8_regardless_of_locale(qapp, tmp_path, encoding):
    """Without an explicit encoding, Windows decodes with the locale codepage (cp1252)."""
    path = tmp_path / 'records.json'
    path.write_text(json.dumps(records_json(msg=NON_ASCII), ensure_ascii=False),
                    encoding=encoding)

    loaded, errors = run_loader(path)

    assert not errors
    name, records = loaded[0]
    assert name == 'records.json'
    assert records[0].message == f'{NON_ASCII} 0'


def test_tab_name_overrides_file_name(qapp, tmp_path):
    path = tmp_path / 'tmp_x7k2.json'
    path.write_text(json.dumps(records_json()), encoding='utf-8')

    loaded, _ = run_loader(path, tab_name='archive.zip')

    assert loaded[0][0] == 'archive.zip'


def test_stdin_json_array(qapp, monkeypatch):
    fake_stdin(monkeypatch, json.dumps(records_json(3, NON_ASCII), ensure_ascii=False)
               .encode('utf-8'))

    loaded, errors = run_loader('-')

    assert not errors
    name, records = loaded[0]
    assert name == 'stdin'
    assert [r.message for r in records] == [f'{NON_ASCII} {i}' for i in range(3)]


def test_stdin_json_stream_falls_back_without_seeking(qapp, monkeypatch):
    """Concatenated objects fail the native loader; the retry must not need a seekable pipe."""
    body = ''.join(json.dumps(r) for r in records_json(2))
    fake_stdin(monkeypatch, body.encode('utf-8'))

    loaded, errors = run_loader('-')

    assert not errors
    assert [r.message for r in loaded[0][1]] == ['hello 0', 'hello 1']


def test_missing_stdin_reports_an_error(qapp, monkeypatch):
    """gui-scripts launchers (pythonw) have no stdin at all."""
    monkeypatch.setattr(sys, 'stdin', None)

    loaded, errors = run_loader('-')

    assert not loaded
    assert 'python -m cutelog2 -' in errors[0]


def test_default_listen_host_is_loopback():
    defaults = {name: default for name, _type, default in OPTION_SPEC}
    assert defaults['listen_host'] == '127.0.0.1'


def test_cmdline_view_only_options(qapp, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['cutelog2', '--no-server', '--tab-name', 'run 1', '-'])

    _overrides, logfiles, run_server, tab_name = parse_cmdline(ROOT_LOG)

    assert logfiles == ['-']
    assert run_server is False
    assert tab_name == 'run 1'


def test_cmdline_defaults(qapp, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['cutelog2'])

    _overrides, logfiles, run_server, tab_name = parse_cmdline(ROOT_LOG)

    assert logfiles == []
    assert run_server is True
    assert tab_name is None


@pytest.fixture
def make_window(qapp, monkeypatch):
    from cutelog2.resources_loader import register_search_paths

    register_search_paths()  # the stylesheets refer to icons via the "icons:" prefix
    monkeypatch.setitem(CONFIG.options, 'listen_host', '127.0.0.1')
    monkeypatch.setitem(CONFIG.options, 'listen_port', 0)
    windows = []

    def _make(*args, **kwargs):
        mw = MainWindow(ROOT_LOG, qapp, *args, **kwargs)
        windows.append(mw)
        return mw

    yield _make
    for mw in windows:
        for lt in mw.findChildren(LoadingThread):
            lt.wait(5000)
        mw.stop_server()
        mw.destroy_all_tabs()
        mw.hide()
        mw.deleteLater()


def test_no_server_starts_no_listener(make_window):
    mw = make_window(run_server=False)

    assert mw.server is None
    assert mw.server_running is False
    assert mw.actionStartStopServer.text() == 'Start server'


def test_server_starts_by_default(make_window):
    mw = make_window()

    assert mw.server_running is True
    assert mw.actionStartStopServer.text() == 'Stop server'


def test_loaded_file_opens_at_first_record(qtbot, tmp_path, make_window):
    """Autoscroll suits a live stream, but a loaded file should start at its first record."""
    path = tmp_path / 'many.json'
    path.write_text(json.dumps(records_json(500)), encoding='utf-8')

    mw = make_window([str(path)], run_server=False, tab_name='review')
    qtbot.waitUntil(lambda: mw.loggerTabWidget.count() == 1, timeout=5000)

    assert mw.loggerTabWidget.tabText(0) == 'review'
    tab = mw.loggers_by_name['review']
    scrollbar = tab.loggerTable.verticalScrollBar()
    # Guards against a vacuous pass: the records must actually overflow the view.
    qtbot.waitUntil(lambda: scrollbar.maximum() > 0, timeout=5000)
    assert tab.autoscroll is False
    assert scrollbar.value() == 0
