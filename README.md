# cutelog2 – GUI for logging
[![PyPI](https://img.shields.io/pypi/v/cutelog2.svg?style=flat-square)](https://pypi.org/project/cutelog2/)
[![Python versions](https://img.shields.io/pypi/pyversions/cutelog2.svg?style=flat-square)](https://pypi.org/project/cutelog2/)
[![CI](https://img.shields.io/github/actions/workflow/status/eachimei/cutelog2/ci.yml?branch=master&style=flat-square&label=CI)](https://github.com/eachimei/cutelog2/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/cutelog2.svg?style=flat-square)](https://github.com/eachimei/cutelog2/blob/master/LICENSE)

cutelog2 is a PyQt6/PySide6 fork of [cutelog](https://github.com/busimus/cutelog) by Alexander Bus,
a graphical log viewer for Python's logging module. It's unaffiliated with the original project;
see the [migration PR](https://github.com/busimus/cutelog/pull/53) for what changed and why.

It can be targeted with a SocketHandler with no additional setup (see [Usage](#usage)).

It can also be used from other languages or logging libraries with little effort (see the [Wiki](../../wiki/Creating-a-client-for-cutelog)).
For example, a Go library [gocutelog](https://github.com/busimus/gocutelog) shows how to enable
regular Go logging libraries to connect to cutelog.

## Features
* Allows any number of simultaneous connections
* Customizable look of log levels and columns, with presets for each
* Filtering based on level and namespace, as well as filtering by searching
* Search through all records or only through filtered ones
* Display extra fields under the message with [Extra mode](../../wiki/Creating-a-client-for-cutelog#extra-mode)
* View exception tracebacks or messages in a separate window
* Dark theme (with its own set of colors for levels)
* Pop tabs out of the window, merge records of multiple tabs into one
* Save/load records to/from a file in JSON format

## Screenshots
Light theme | Dark theme
------------|-----------
<img src="https://raw.githubusercontent.com/eachimei/cutelog2/master/screenshots/main_light.png" width="240"> | <img src="https://raw.githubusercontent.com/eachimei/cutelog2/master/screenshots/main_dark.png" width="240">

## Installation
**If you're using Linux**, install PySide6 (or PyQt6) from your package manager before installing cutelog2 (package name is probably ``python3-pyside6`` or ``python-pyside6``). Or just run ``pip install pyside6`` to install it from pip, which is sub-optimal.

```
$ pip install cutelog2
```
Or install the latest development version from the source:

```
$ pip install git+https://github.com/eachimei/cutelog2.git
```

### Choosing a Qt binding
cutelog2 runs on either PySide6 or PyQt6, and both are covered by CI. PySide6 is installed
by default because it's [LGPLv3](https://doc.qt.io/qtforpython-6/licenses.html), so it
places no licensing obligation on you; PyQt6 is
[GPLv3 or commercial](https://riverbankcomputing.com/commercial/pyqt).

To use PyQt6 instead:

```
$ pip install cutelog2[pyqt6]
```

If both are installed, cutelog2 prefers PySide6. Override with the ``QT_API`` environment
variable, which accepts ``pyside6`` or ``pyqt6``:

```
$ QT_API=pyqt6 cutelog2
```

### Requirements
* Python 3.10 (or newer)
* PySide6 or PyQt6
* [QtPy](https://github.com/spyder-ide/qtpy) 2.4 or newer

### Desktop entry (Linux)
The wheel deliberately doesn't install into ``share/`` — that only works for system-wide
installs and silently does nothing inside a virtualenv or pipx environment. Distribution
packagers should install ``share/cutelog2.desktop`` and ``share/cutelog2.png`` from the sdist.
To add the menu entry manually:

```
$ xdg-desktop-menu install --novendor share/cutelog2.desktop
$ xdg-icon-resource install --novendor --size 128 share/cutelog2.png cutelog2
```

## Usage
1. Start `cutelog2`
2. Put the following into your code:
```python
import logging
from logging.handlers import SocketHandler

log = logging.getLogger('Root logger')
log.setLevel(1)  # to send all records to cutelog
socket_handler = SocketHandler('127.0.0.1', 19996)  # default listening address
log.addHandler(socket_handler)
log.info('Hello world!')
```
Afterwards it's recommended to designate different loggers for different parts of your program with `log_2 = log.getChild("Child logger")`.
This will create "log namespaces" which allow you to filter out messages from various subsystems of your program.

## Attributions
Free software used:
* Qt via either:
    * [PyQt6](https://riverbankcomputing.com/software/pyqt/intro) - GPLv3 License, Copyright (c) 2024 Riverbank Computing Limited <info@riverbankcomputing.com>
    * [PySide6](https://wiki.qt.io/Qt_for_Python) - LGPLv3 License, Copyright (C) 2015 The Qt Company Ltd (http://www.qt.io/licensing/)
* [QtPy](https://github.com/spyder-ide/qtpy) - MIT License, Copyright (c) 2011- QtPy contributors and others
* [jsonstream](https://github.com/Dunes/json_stream) - MIT License, Copyright (c) 2020 Dunes
* [ion-icons](https://github.com/ionic-team/ionicons) - MIT License, Copyright (c) 2015-present Ionic (http://ionic.io/)

And thanks to [logview](https://pythonhosted.org/logview/) by Vinay Sajip for UI inspiration.

### Copyright and license
This program is released under the MIT License (see LICENSE file).

Copyright © 2023 bus and contributors.
