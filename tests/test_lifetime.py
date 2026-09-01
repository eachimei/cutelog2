"""Object-lifetime and sustained-load tests.

These target the area where PyQt6 and PySide6 diverge most: ownership of QObjects on the
Python side, and teardown of QThreads. Short functional tests pass under either binding
even when lifetime handling is wrong, because nothing forces collection or runs long
enough for a leak to show.
"""

import gc
import logging
import weakref
from logging.handlers import SocketHandler

import pytest

from cutelog2.config import CONFIG, ROOT_LOG
from cutelog2.listener import LogServer


@pytest.fixture
def server(qtbot, main_window_stub, monkeypatch):
    monkeypatch.setitem(CONFIG.options, 'listen_host', '127.0.0.1')
    monkeypatch.setitem(CONFIG.options, 'listen_port', 0)
    monkeypatch.setitem(CONFIG.options, 'benchmark', False)

    connections = []
    received = []

    def on_connection(conn, conn_id):
        connections.append(conn)
        conn.new_record.connect(received.append)

    srv = LogServer(main_window_stub, on_connection, ROOT_LOG)
    srv.start()
    assert srv.isListening()
    srv.connections = connections
    srv.received = received
    yield srv
    srv.close_server()


def make_log_record(message):
    return logging.LogRecord('soak', logging.INFO, __file__, 1, message, None, None)


def connect_client(qtbot, server):
    handler = SocketHandler('127.0.0.1', server.serverPort())
    with qtbot.waitSignal(server.newConnection, timeout=5000):
        handler.createSocket()
    return handler


def test_finished_connection_is_released(qtbot, server):
    """A disconnected client must not leave its thread object alive.

    deleteLater only schedules destruction, so the event loop has to run before the
    weakref can clear -- that scheduling is precisely what differs between bindings.
    """
    handler = connect_client(qtbot, server)
    qtbot.waitUntil(lambda: bool(server.connections), timeout=5000)
    conn = server.connections[0]
    ref = weakref.ref(conn)

    with qtbot.waitSignal(conn.connection_finished, timeout=5000):
        handler.close()

    qtbot.waitUntil(lambda: not server.threads, timeout=5000)

    del conn
    server.connections.clear()
    # deleteLater is queued; give the event loop a chance to actually run it.
    qtbot.wait(50)
    gc.collect()

    assert ref() is None, 'connection thread outlived its connection'


def test_server_drops_all_connection_threads_on_close(qtbot, main_window_stub, monkeypatch):
    """close_server() must leave nothing behind, even with clients still attached."""
    monkeypatch.setitem(CONFIG.options, 'listen_host', '127.0.0.1')
    monkeypatch.setitem(CONFIG.options, 'listen_port', 0)
    monkeypatch.setitem(CONFIG.options, 'benchmark', False)

    connections = []
    srv = LogServer(main_window_stub, lambda c, i: connections.append(c), ROOT_LOG)
    srv.start()

    handlers = []
    for _ in range(3):
        handlers.append(connect_client(qtbot, srv))
    qtbot.waitUntil(lambda: len(srv.threads) == 3, timeout=5000)

    refs = [weakref.ref(t) for t in srv.threads]

    srv.close_server()
    for handler in handlers:
        handler.close()

    connections.clear()
    qtbot.wait(50)
    gc.collect()

    assert srv.threads == [], 'server still tracks connection threads after close'
    alive = [r for r in refs if r() is not None]
    assert not alive, f'{len(alive)} connection thread(s) survived close_server()'


def test_repeated_connect_disconnect_cycles_do_not_accumulate(qtbot, server):
    """Churn connections and assert the server's thread list returns to empty each time.

    A leak here is invisible in a single-connection test but unbounded in real use, where
    clients reconnect for the lifetime of the process.
    """
    for _ in range(10):
        handler = connect_client(qtbot, server)
        qtbot.waitUntil(lambda: bool(server.threads), timeout=5000)
        handler.close()
        qtbot.waitUntil(lambda: not server.threads, timeout=5000)

    server.connections.clear()
    qtbot.wait(50)
    gc.collect()
    assert server.threads == []


def test_sustained_record_load(qtbot, server):
    """Push a few thousand records through concurrent clients.

    Cross-thread signal delivery under load is where ownership bugs surface as dropped
    records or a crash, rather than as a clean failure.
    """
    clients = 3
    per_client = 500
    handlers = [connect_client(qtbot, server) for _ in range(clients)]
    qtbot.waitUntil(lambda: len(server.threads) == clients, timeout=5000)

    try:
        for i in range(per_client):
            for handler in handlers:
                handler.send(handler.makePickle(make_log_record(f'record {i}')))

        expected = clients * per_client
        qtbot.waitUntil(lambda: len(server.received) >= expected, timeout=60000)
    finally:
        for handler in handlers:
            handler.close()

    assert len(server.received) == clients * per_client
    assert all(r.message.startswith('record ') for r in server.received)
