import datetime
import logging
import pickle
import struct
from logging.handlers import SocketHandler

import pytest

from cutelog2.config import CONFIG, ROOT_LOG
from cutelog2.listener import LogServer, safe_pickle_loads

EXPLOITED = []


def _exploit(*args):
    EXPLOITED.append(args)
    return 'exploited'


class Exploit:
    """Unpickling this with plain pickle.loads calls _exploit -- a stand-in for os.system."""

    def __reduce__(self):
        return (_exploit, ('payload ran',))


class Custom:
    def __init__(self):
        self.value = 42


@pytest.fixture(autouse=True)
def _reset_exploited():
    EXPLOITED.clear()


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


def test_exploit_payload_is_real():
    """Guards the tests below against a vacuous pass: plain pickle does run the payload."""
    pickle.loads(pickle.dumps({'msg': Exploit()}, 1))
    assert EXPLOITED == [('payload ran',)]


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_payload_cannot_run_code(protocol):
    loaded = safe_pickle_loads(pickle.dumps({'msg': 'hi', 'evil': Exploit()}, protocol))

    assert EXPLOITED == []
    assert loaded['msg'] == 'hi'
    assert repr(loaded['evil']) == f'<{__name__}._exploit>'


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_unknown_classes_become_placeholders(protocol):
    loaded = safe_pickle_loads(pickle.dumps({'obj': Custom(), 'items': [Custom()]}, protocol))

    # Protocols 0-1 route through copyreg._reconstructor; the name must still be Custom's.
    assert repr(loaded['obj']) == f'<{__name__}.Custom>'
    assert not hasattr(loaded['obj'], 'value')
    assert [repr(i) for i in loaded['items']] == [f'<{__name__}.Custom>']


def test_reconstructor_with_non_placeholder_class_stays_inert():
    class Sneaky:
        def __reduce__(self):
            import copyreg
            return (copyreg._reconstructor, (datetime.timedelta, object, None))

    loaded = safe_pickle_loads(pickle.dumps(Sneaky(), 2))

    assert repr(loaded) == '<copyreg._reconstructor>'


def test_socket_handler_payload_round_trips():
    handler = SocketHandler('127.0.0.1', 0)
    record = make_log_record('plain')
    record.when = datetime.datetime(2026, 1, 2, 3, 4, 5)
    data = handler.makePickle(record)[4:]  # strip the length prefix

    loaded = safe_pickle_loads(data)

    assert loaded == pickle.loads(data)
    assert loaded['when'] == datetime.datetime(2026, 1, 2, 3, 4, 5)


def test_socket_handler_custom_extra_shows_class_name():
    handler = SocketHandler('127.0.0.1', 0)
    record = make_log_record('with extra')
    record.custom = Custom()

    loaded = safe_pickle_loads(handler.makePickle(record)[4:])

    assert repr(loaded['custom']) == f'<{__name__}.Custom>'


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_safe_types_round_trip(protocol):
    import decimal

    value = {
        'dt': datetime.datetime(2026, 1, 2, tzinfo=datetime.timezone.utc),
        'd': datetime.date(2026, 1, 2), 't': datetime.time(3, 4), 'td': datetime.timedelta(5),
        'dec': decimal.Decimal('1.5'), 's': {1, 2}, 'fs': frozenset({3}), 'b': b'\xff\x00',
    }
    assert safe_pickle_loads(pickle.dumps(value, protocol)) == value


def test_codecs_encode_is_restricted_to_latin1():
    class Sneaky:
        def __reduce__(self):
            import _codecs
            return (_codecs.encode, ('x', 'rot13'))

    with pytest.raises(pickle.UnpicklingError):
        safe_pickle_loads(pickle.dumps(Sneaky(), 2))


def test_exploit_over_tcp_still_delivers_record(qtbot, server):
    import socket

    payload = pickle.dumps({'msg': 'carrier', 'levelname': 'INFO', 'evil': Exploit()}, 1)
    sock = socket.create_connection(('127.0.0.1', server.serverPort()))
    try:
        qtbot.waitUntil(lambda: bool(server.connections), timeout=5000)
        conn = server.connections[0]
        with qtbot.waitSignal(conn.new_record, timeout=5000):
            sock.sendall(struct.pack('>L', len(payload)) + payload)
    finally:
        sock.close()

    assert EXPLOITED == []
    assert server.received[0].message == 'carrier'
    assert server.received[0].evil == f'<{__name__}._exploit>'
