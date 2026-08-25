import re

import pytest

from cutelog.resources_loader import APP_ICON_PATH, ICON_DIR, RESOURCE_DIR, UI_DIR, get_ui_path

UI_FILES = ['about_dialog.ui', 'logger.ui', 'settings_dialog.ui']
STYLESHEETS = ['dark_theme.qss', 'light_theme.qss']
URL_RE = re.compile(r'url\(([^)]+)\)')


def test_resource_dir_exists():
    assert RESOURCE_DIR.is_dir()
    assert APP_ICON_PATH.is_file()


@pytest.mark.parametrize('name', UI_FILES)
def test_ui_files_present(name):
    assert (UI_DIR / name).is_file()
    assert get_ui_path(name) == str(UI_DIR / name)


def test_get_ui_path_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        get_ui_path('does_not_exist.ui')


@pytest.mark.parametrize('name', STYLESHEETS)
def test_stylesheet_icon_urls_resolve(name):
    from cutelog.resources_loader import get_stylesheet

    urls = URL_RE.findall(get_stylesheet(name))
    assert urls, f'{name} has no url() references'
    for url in urls:
        prefix, _, relative = url.partition(':')
        assert prefix == 'icons', f'unexpected url prefix in {name}: {url}'
        assert (ICON_DIR / relative).is_file(), f'{name} references missing icon {url}'


def test_no_qt_resource_paths_remain():
    """The :/ resource scheme is gone; nothing may still reference it."""
    package_dir = RESOURCE_DIR.parent
    offenders = []
    for path in list(package_dir.glob('*.py')) + list(RESOURCE_DIR.glob('*.qss')):
        if ':/' in path.read_text(encoding='utf-8'):
            offenders.append(path.name)
    assert offenders == []
