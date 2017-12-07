Contributing
============

Contributions are welcome! Development happens at
`GitHub <https://github.com/pytries/marisa-trie>`_. Feel free to submit
ideas, bug reports and pull requests.

If you found a bug in a C++ part please report it to the original
`bug tracker <https://github.com/s-yata/marisa-trie/issues>`_.

Navigating the source code
--------------------------

There are 4 folders in repository:

* ``bench`` -- benchmarks & benchmark data;
* ``lib`` -- original unmodified `marisa-trie`_ C++ library which is a git
  submodule; if something is have to be fixed in this library
  consider fixing it in the original repo;
* ``src`` -- wrapper code; ``src/marisa_trie.pyx`` is a wrapper implementation;
  ``src/*.pxd`` files are Cython headers for corresponding C++ headers;
  ``src/*.cpp`` files are the pre-built extension code and shouldn't be
  modified directly (they should be updated via ``update_cpp.sh`` script).
* ``tests`` -- the test suite.

.. _marisa-trie: https://github.com/s-yata/marisa-trie

Running tests and benchmarks
----------------------------

Make sure `tox`_ is installed and run

::

    $ tox

from the source checkout. Tests should pass under Python 2.7,
3.4 and 3.5.

In order to run benchmarks, type

::

    $ tox -c bench.ini


.. _cython: http://cython.org
.. _tox: http://tox.testrun.org
