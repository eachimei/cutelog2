import pytest
from qtpy.QtGui import QValidator

from cutelog.level_edit_dialog import LevelNameValidator
from cutelog.settings_dialog import TimeFormatValidator


@pytest.mark.parametrize('name, expected', [
    ('info', QValidator.State.Acceptable),
    ('NEWLEVEL', QValidator.State.Acceptable),
    ('DEBUG', QValidator.State.Intermediate),
])
def test_level_name_validator(qtbot, name, expected):
    validator = LevelNameValidator(None, ['DEBUG', 'INFO'])
    state, _text, _pos = validator.validate(name, 0)
    assert state == expected


@pytest.mark.parametrize('fmt, expected', [
    ('%H:%M:%S', QValidator.State.Acceptable),
    ('', QValidator.State.Acceptable),
])
def test_time_format_validator(qtbot, fmt, expected):
    validator = TimeFormatValidator(None)
    state, _text, _pos = validator.validate(fmt, 0)
    assert state == expected


def test_validator_states_are_qt_enum_members(qtbot):
    validator = TimeFormatValidator(None)
    state, _text, _pos = validator.validate('%Y', 0)
    assert isinstance(state, QValidator.State)
