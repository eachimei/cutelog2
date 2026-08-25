"""Locks in the search-filter behaviour that used to be implemented with QRegExp."""
import pytest


def accepted_messages(filter_model):
    return [filter_model.sourceModel().get_record(
        filter_model.mapToSource(filter_model.index(row, 0)).row()).message
        for row in range(filter_model.rowCount())]


@pytest.fixture
def populated(filter_model, record_model, make_record):
    for message in ['alpha', 'Alpha', 'alphabet', 'beta', 'gamma delta']:
        record_model.add_record(make_record(message=message))
    return filter_model


def test_no_filter_accepts_everything(populated):
    assert len(accepted_messages(populated)) == 5


def test_plain_substring_case_insensitive(populated):
    populated.set_filter('alpha', regexp=False, wildcard=False, casesensitive=False)
    assert accepted_messages(populated) == ['alpha', 'Alpha', 'alphabet']


def test_plain_substring_case_sensitive(populated):
    populated.set_filter('Alpha', regexp=False, wildcard=False, casesensitive=True)
    assert accepted_messages(populated) == ['Alpha']


def test_regex_matches_whole_string_only(populated):
    """QRegExp.exactMatch() is gone; the anchored pattern must preserve its semantics."""
    populated.set_filter('alpha', regexp=True, wildcard=False, casesensitive=True)
    assert accepted_messages(populated) == ['alpha']


def test_regex_with_explicit_wildcards_matches_prefix(populated):
    populated.set_filter('alpha.*', regexp=True, wildcard=False, casesensitive=True)
    assert accepted_messages(populated) == ['alpha', 'alphabet']


def test_regex_is_case_insensitive_when_asked(populated):
    populated.set_filter('alpha', regexp=True, wildcard=False, casesensitive=False)
    assert accepted_messages(populated) == ['alpha', 'Alpha']


def test_wildcard_matches_whole_string(populated):
    populated.set_filter('alpha*', regexp=False, wildcard=True, casesensitive=True)
    assert accepted_messages(populated) == ['alpha', 'alphabet']


def test_wildcard_single_character(populated):
    populated.set_filter('alph?', regexp=False, wildcard=True, casesensitive=True)
    assert accepted_messages(populated) == ['alpha']


def test_empty_regex_falls_back_to_substring(populated):
    populated.set_filter('', regexp=True, wildcard=False, casesensitive=True)
    assert len(accepted_messages(populated)) == 5


def test_clear_filter_restores_everything(populated):
    populated.set_filter('alpha', regexp=True, wildcard=False, casesensitive=True)
    assert len(accepted_messages(populated)) == 1
    populated.clear_filter()
    assert len(accepted_messages(populated)) == 5


def test_level_filter_excludes_disabled_levels(filter_model, record_model, make_record):
    record_model.add_record(make_record(message='kept', levelname='INFO'))
    record_model.add_record(make_record(message='dropped', levelname='DEBUG'))
    record_model.level_filter.levels['DEBUG'].set_enabled(False)
    filter_model.invalidate()
    assert accepted_messages(filter_model) == ['kept']
