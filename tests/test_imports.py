import importlib
import pkgutil

import pytest

import cutelog2

MODULES = sorted(m.name for m in pkgutil.iter_modules(cutelog2.__path__)
                 if m.name != '__main__')


@pytest.mark.parametrize('name', MODULES)
def test_module_imports(name):
    """Catches enums evaluated at import time, e.g. in method default arguments."""
    importlib.import_module(f'cutelog2.{name}')


def test_qt_binding_is_qt6():
    import qtpy

    assert qtpy.PYQT6 or qtpy.PYSIDE6
