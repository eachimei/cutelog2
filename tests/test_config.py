from qtpy.QtCore import QCoreApplication

from cutelog2.config import CONFIG, OPTION_SPEC, Config


def test_qt_application_identity():
    assert QCoreApplication.applicationName() == 'cutelog2'
    assert QCoreApplication.applicationVersion()


def test_settings_are_sandboxed(settings_dir):
    expected = settings_dir.replace('\\', '/')
    assert CONFIG.qsettings.fileName().replace('\\', '/').startswith(expected)


def test_every_option_has_a_value():
    for name, type_, _default in OPTION_SPEC:
        assert name in CONFIG.options
        assert isinstance(CONFIG[name], type_)


def test_bool_options_round_trip_through_qsettings():
    """QSettings stores bools as strings; the coercion in load_options must survive that."""
    CONFIG.set_option('dark_theme_default', True)
    CONFIG.sync()
    reloaded = Config()
    assert reloaded['dark_theme_default'] is True

    CONFIG.set_option('dark_theme_default', False)
    CONFIG.sync()
    reloaded = Config()
    assert reloaded['dark_theme_default'] is False


def test_int_options_round_trip_through_qsettings():
    CONFIG.set_option('logger_row_height', 23)
    CONFIG.sync()
    assert Config()['logger_row_height'] == 23


def test_data_path_is_resolvable():
    assert Config.get_data_path()


def test_listen_address():
    host, port = CONFIG.listen_address
    assert isinstance(host, str)
    assert isinstance(port, int)
