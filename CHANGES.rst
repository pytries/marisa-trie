
CHANGES
=======

0.3.8 (2013-01-03)
------------------

* Rebuild wrapper with Cython pre-0.18;
* update benchmarks.

0.3.7 (2012-09-21)
------------------

* Update bundled marisa-trie C++ library (this may fix more mingw issues);
* Python 3.3 support is back.

0.3.6 (2012-09-05)
------------------

* much faster (3x-7x) ``.items()`` and ``.keys()`` methods for all tries;
  faster (up to 3x) ``.prefixes()`` method for ``Trie``.

0.3.5 (2012-08-30)
------------------

* Pickling of RecordTrie is fixed (thanks lazarou for the report);
* error messages should become more useful.

0.3.4 (2012-08-29)
------------------

* Issues with mingw32 should be resolved (thanks Susumu Yata).

0.3.3 (2012-08-27)
------------------

* ``.get(key, default=None)`` method for ``BytesTrie`` and ``RecordTrie``;
* small README improvements.

0.3.2 (2012-08-26)
------------------

* Small code cleanup;
* ``load``, ``read`` and ``mmap`` methods returns 'self';
* I can't run tests (via tox) under Python 3.3 so it is
  removed from supported versions for now.

0.3.1 (2012-08-23)
------------------

* ``.prefixes()`` support for RecordTrie and BytesTrie.

0.3 (2012-08-23)
----------------

* RecordTrie and BytesTrie are introduced;
* IntTrie class is removed (probably temporary?);
* dumps/loads methods are renamed to tobytes/frombytes;
* benchmark & tests improvements;
* support for MARISA-trie config options is added.

0.2 (2012-08-19)
------------------

* Pickling/unpickling support;
* dumps/loads methods;
* python 3.3 workaround;
* improved tests;
* benchmarks.

0.1 (2012-08-17)
----------------

Initial release.
