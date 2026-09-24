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


def test_package_does_not_import_dunder_main():
    """Otherwise every `python -m cutelog2` warns that __main__ was already imported."""
    import subprocess
    import sys

    code = "import sys, cutelog2; sys.exit('cutelog2.__main__' in sys.modules)"
    assert subprocess.run([sys.executable, '-c', code]).returncode == 0
