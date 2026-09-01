import atexit
from contextlib import ExitStack
from importlib.resources import as_file, files
from pathlib import Path

from qtpy.QtCore import QDir

# as_file() materializes the package data if it isn't already on disk; Qt needs real paths.
_file_manager = ExitStack()
atexit.register(_file_manager.close)

RESOURCE_DIR: Path = _file_manager.enter_context(as_file(files(__package__) / 'resources'))
UI_DIR = RESOURCE_DIR / 'ui'
ICON_DIR = RESOURCE_DIR / 'icons'
APP_ICON_PATH = RESOURCE_DIR / 'images' / 'cutelog.png'


def register_search_paths():
    """Lets stylesheets refer to icons as url(icons:<theme>/<name>.svg)."""
    QDir.addSearchPath('icons', str(ICON_DIR))


def get_ui_path(name):
    path = UI_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f'ui file not found: "{path}"')
    return str(path)


def get_stylesheet(name):
    path = RESOURCE_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f'stylesheet not found: "{path}"')
    return path.read_text(encoding='utf-8')
