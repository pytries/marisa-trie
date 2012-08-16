marisa-trie
===========

MARISA-Trie structure for Python (2.x and 3.x).
Uses `marisa-trie`_.

There are official SWIG-based Python bindings included
in library distribution; this package provides an alternative
unofficial Cython-based pip-installable Python bindings.

.. _marisa-trie: https://code.google.com/p/marisa-trie/

Installation
============

::

    pip install marisa-trie

Usage
=====

Create a new trie::

    >>> from marisa_trie import Trie
    >>> trie = Trie()


Contributing
============

Development happens at github and bitbucket:

* https://github.com/kmike/marisa-trie
* https://bitbucket.org/kmike/marisa-trie

The main issue tracker is at github.

Feel free to submit ideas, bugs, pull requests (git or hg) or
regular patches.


Running tests and benchmarks
----------------------------

Make sure `tox`_ is installed and run

::

    $ tox

from the source checkout. Tests should pass under python 2.6, 2.7, 3.2 and 3.3.

.. note::

    At the moment of writing the latest pip release (1.1) does not
    support Python 3.3; in order to run tox tests under Python 3.3
    find the "virtualenv_support" directory in site-packages
    (of the env you run tox from) and place an sdist zip/tarball of the newer
    pip (from github) there.

::

    $ tox -c bench.ini

runs benchmarks.

.. _cython: http://cython.org
.. _tox: http://tox.testrun.org

Authors & Contributors
----------------------

* Mikhail Korobov <kmike84@gmail.com>

This module is based on `marisa-trie`_ C library.

License
=======

Licensed under MIT License.
