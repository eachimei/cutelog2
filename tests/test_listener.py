import logging
import struct
from logging.handlers import SocketHandler

import pytest

from cutelog.config import CONFIG, ROOT_LOG
from cutelog.listener import LogServer


@pytest.fixture
def server(qtbot, main_window_stub, monkeypatch):
    monkeypatch.setitem(CONFIG.options, 'listen_host', '127.0.0.1')
    monkeypatch.setitem(CONFIG.options, 'listen_port', 0)  # let the OS pick a free port
    monkeypatch.setitem(CONFIG.options, 'benchmark', False)

    received = []
    connections = []

    def on_connection(conn, conn_id):
        connections.append(conn)
        conn.new_record.connect(received.append)

    srv = LogServer(main_window_stub, on_connection, ROOT_LOG)
    srv.start()
    assert srv.isListening()
    srv.received = received
    srv.connections = connections
    yield srv
    srv.close_server()


def send(handler, record):
    handler.send(handler.makePickle(record))


def make_log_record(message):
    return logging.LogRecord('test.namespace', logging.WARNING, __file__, 1, message, None, None)


def test_record_arrives_over_tcp(qtbot, server):
    handler = SocketHandler('127.0.0.1', server.serverPort())
    try:
        with qtbot.waitSignal(server.newConnection, timeout=5000):
            handler.createSocket()
        qtbot.waitUntil(lambda: bool(server.connections), timeout=5000)
        conn = server.connections[0]
        with qtbot.waitSignal(conn.new_record, timeout=5000):
            send(handler, make_log_record('over the wire'))
    finally:
        handler.close()

    assert server.received[0].message == 'over the wire'
    assert server.received[0].levelname == 'WARNING'
    assert server.received[0].name == 'test.namespace'


def test_client_disconnect_finishes_the_connection(qtbot, server):
    handler = SocketHandler('127.0.0.1', server.serverPort())
    with qtbot.waitSignal(server.newConnection, timeout=5000):
        handler.createSocket()
    qtbot.waitUntil(lambda: bool(server.connections), timeout=5000)
    conn = server.connections[0]

    with qtbot.waitSignal(conn.connection_finished, timeout=5000):
        handler.close()


def test_malformed_length_prefix_does_not_crash(qtbot, server):
    import socket

    sock = socket.create_connection(('127.0.0.1', server.serverPort()))
    try:
        qtbot.waitUntil(lambda: bool(server.connections), timeout=5000)
        conn = server.connections[0]
        sock.sendall(struct.pack('>L', 4) + b'junk')
        with qtbot.waitSignal(conn.connection_finished, timeout=5000):
            sock.close()
    finally:
        sock.close()
