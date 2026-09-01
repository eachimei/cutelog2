.. contents:: Table of contents
   :depth: 2

========
cutelog2
========

.. image:: https://img.shields.io/pypi/v/cutelog2.svg?style=flat-square
   :target: https://pypi.org/project/cutelog2/
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/cutelog2.svg?style=flat-square
   :target: https://pypi.org/project/cutelog2/
   :alt: Python versions

.. image:: https://img.shields.io/github/actions/workflow/status/eachimei/cutelog2/ci.yml?branch=master&style=flat-square&label=CI
   :target: https://github.com/eachimei/cutelog2/actions/workflows/ci.yml
   :alt: CI

.. image:: https://img.shields.io/pypi/l/cutelog2.svg?style=flat-square
   :target: https://github.com/eachimei/cutelog2/blob/master/LICENSE
   :alt: License

cutelog2 is a PyQt6/PySide6 fork of `cutelog <https://github.com/busimus/cutelog>`_ by
Alexander Bus, a graphical log viewer for Python's standard logging module. It's
unaffiliated with the original project; see the
`migration PR <https://github.com/busimus/cutelog/pull/53>`_ for what changed and why.
It can be targeted with a SocketHandler with no additional setup (see Usage_).
cutelog2 is cross-platform, although it's mainly written and optimized for Linux.

Features
========
* Allows any number of simultaneous connections
* Customizable look of log levels and columns, with presets for each
* Filtering based on level and namespace, as well as filtering by searching
* Search through all records or only through filtered ones
* Display extra fields under the message with `Extra mode <https://github.com/busimus/cutelog/wiki/Creating-a-client-for-cutelog#extra-mode>`_
* View exception tracebacks or messages in a separate window
* Dark theme (with its own set of colors for levels)
* Pop tabs out of the window, merge records of multiple tabs into one
* Save/load records to/from a file in JSON format

Installation
============
**If you're using Linux**, install PySide6 (or PyQt6) from your package manager before installing cutelog2 (package name is probably ``python3-pyside6`` or ``python-pyside6``). Or just run ``pip install pyside6`` to install it from pip, which is sub-optimal.
::

    $ pip install --upgrade cutelog2

Or install the latest development version from the source::

    $ pip install git+https://github.com/eachimei/cutelog2.git

Choosing a Qt binding
---------------------
cutelog2 runs on either PySide6 or PyQt6, and both are covered by CI. PySide6 is installed
by default because it is LGPLv3, so it places no licensing obligation on you; PyQt6 is
GPLv3 or commercial.

To use PyQt6 instead::

    $ pip install cutelog2[pyqt6]

If both are installed, cutelog2 prefers PySide6. Override with the ``QT_API`` environment
variable, which accepts ``pyside6`` or ``pyqt6``::

    $ QT_API=pyqt6 cutelog2

Requirements
------------
* Python 3.10 (or newer)
* PySide6 or PyQt6
* QtPy

Usage
=====
1. Start `cutelog2`

2. Put the following into your code:

.. code-block :: python

    import logging
    from logging.handlers import SocketHandler

    log = logging.getLogger('Root logger')
    log.setLevel(1)  # to send all messages to cutelog
    socket_handler = SocketHandler('127.0.0.1', 19996)  # default listening address
    log.addHandler(socket_handler)
    log.info('Hello world!')

Afterwards it's recommended to designate different loggers for different parts of your program with `log_2 = log.getChild("Child logger")`.
This will create "log namespaces" which allow you to filter out messages from various subsystems of your program.

Code, issues, changelog
=======================
Visit the project's `GitHub page <https://github.com/eachimei/cutelog2>`_.
