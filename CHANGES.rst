
CHANGES
=======

1.3.0 (2025-xx-xx)
------------------

* Updated ``libmarisa-trie`` to the latest version (0.2.7) (#116).
* Dropped Python 3.7 support (#112).
* Added Python 3.13 support (#112).
* Rebuild Cython wrapper with Cython 3.1.1 (#117).

1.2.1 (2024-10-12)
------------------

* Publish Python 3.13 wheels (only CPython ones, PyPy ones are skipped until https://github.com/pypa/distutils/issues/283 is fixed).
* Rebuild Cython wrapper with Cython 3.0.11.

1.2.0 (2024-06-05)
------------------

* Added Python 3.13 support (#105).
* Rebuild Cython wrapper with Cython 3.0.10 (#105).

1.1.1 (2024-05-06)
------------------

* Publish Linux aarch64 wheels (#101).

1.1.0 (2023-10-06)
------------------

* Added Python 3.12 support.

1.0.0 (2023-09-03)
------------------

* Dropped Python 2.7, 3.4, 3.5, 3.6 support.
* Added ``Trie.map()`` (#90).
* Rebuilt Cython wrapper with Cython 3.0.2.
* Fixed benchmark documentation typos (#89).

0.8.0 (2023-03-25)
------------------

* Add ``Trie.iter_prefixes_with_ids()`` method to return ``(prefix, id)`` pairs (#83).
* Rebuild Cython wrapper with Cython 0.29.33 (#88).

0.7.8 (2022-10-25)
------------------

* Added Python 3.11 support.
* Rebuild Cython wrapper with Cython 0.29.32.

0.7.7 (2021-08-04)
------------------

* Restored Python 2.7 support.
* Fixed README image references not working on Windows.

0.7.6 (2021-07-28)
------------------

* Wheels are now published for all platforms.
* Fixed ``ResourceWarning: unclosed file`` in ``setup.py``.
* Run ``black`` on the entire source code.
* Moved the QA/CI to GitHub.
* Rebuild Cython wrapper with Cython 0.29.24.
* Updated ``libmarisa-trie`` to the latest version (0.2.6).
* Fixed failing tests and usage of deprecated methods.
* Expanded supported Python version (2.7, 3.4 - 3.10).

0.7.5 (2018-04-10)
------------------

* Removed redundant ``DeprecationWarning`` messages in ``Trie.save`` and
  ``Trie.load``.
* Dropped support for Python 2.6.
* Rebuild Cython wrapper with Cython 0.28.1.

0.7.4 (2017-03-27)
------------------

* Fixed packaging issue, ``MANIFEST.in`` was not updated after ``libmarisa-trie``
  became a submodule.

0.7.3 (2017-02-14)
------------------

* Added ``BinaryTrie`` for storing arbitrary sequences of bytes, e.g. IP
  addresses (thanks Tomasz Melcer);
* Deprecated ``Trie.has_keys_with_prefix`` which can be trivially implemented in
  terms of ``Trie.iterkeys``;
* Deprecated ``Trie.read`` and ``Trie.write`` which onlywork for "real" files
  and duplicate the functionality of ``load`` and ``save``. See issue #31 on
  GitHub;
* Updated ``libmarisa-trie`` to the latest version. Yay, 64-bit Windows support.
* Rebuilt Cython wrapper with Cython 0.25.2.

0.7.2 (2015-04-21)
------------------

* packaging issue is fixed.

0.7.1 (2015-04-21)
------------------

* setup.py is switched to setuptools;
* a tiny speedup;
* wrapper is rebuilt with Cython 0.22.

0.7 (2014-12-15)
----------------

* ``trie1 == trie2`` and ``trie1 != trie2`` now work (thanks Sergei Lebedev);
* ``for key in trie:`` is fixed (thanks Sergei Lebedev);
* wrapper is rebuilt with Cython 0.21.1 (thanks Sergei Lebedev);
* https://bitbucket.org/kmike/marisa-trie repo is no longer supported.

0.6 (2014-02-22)
----------------

* New ``Trie`` methods: ``__getitem__``, ``get``, ``items``, ``iteritems``.
  ``trie[u'key']`` is now the same as ``trie.key_id(u'key')``.
* small optimization for ``BytesTrie.get``.
* wrapper is rebuilt with Cython 0.20.1.

0.5.3 (2014-02-08)
------------------

* small ``Trie.restore_key`` optimization (it should work 5-15% faster)

0.5.2 (2014-02-08)
------------------

* fix ``Trie.restore_key`` method - it was reading past declared string length;
* rebuild wrapper with Cython 0.20.

0.5.1 (2013-10-03)
------------------

* ``has_keys_with_prefix(prefix)`` method (thanks
  `Matt Hickford <https://github.com/matt-hickford>`_)

0.5 (2013-05-07)
----------------

* ``BytesTrie.iterkeys``, ``BytesTrie.iteritems``,
  ``RecordTrie.iterkeys`` and ``RecordTrie.iteritems`` methods;
* wrapper is rebuilt with Cython 0.19;
* ``value_separator`` parameter for ``BytesTrie`` and ``RecordTrie``.

0.4 (2013-02-28)
----------------

* improved trie building: ``weights`` optional parameter;
* improved trie building: unnecessary input sorting is removed;
* wrapper is rebuilt with Cython 0.18;
* bundled marisa-trie C++ library is updated to svn r133.

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
