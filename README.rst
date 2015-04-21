marisa-trie
===========

.. image:: https://travis-ci.org/kmike/marisa-trie.png?branch=master
    :target: https://travis-ci.org/kmike/marisa-trie

Static memory-efficient Trie-like structures for Python (2.x and 3.x).

String data in a MARISA-trie may take up to 50x-100x less memory than
in a standard Python dict; the raw lookup speed is comparable; trie also
provides fast advanced methods like prefix search.

Based on `marisa-trie`_ C++ library.

.. note::

    There are official SWIG-based Python bindings included
    in C++ library distribution; this package provides an alternative
    Cython-based pip-installable Python bindings.

.. _marisa-trie: https://code.google.com/p/marisa-trie/

Installation
============

::

    pip install marisa-trie

Usage
=====

There are several Trie classes in this package:

* ``marisa_trie.Trie`` - read-only trie-based data structure that maps
  unicode keys to auto-generated unique IDs;

* ``marisa_trie.RecordTrie`` - read-only trie-based data structure that
  maps unicode keys to lists of data tuples. All tuples must be of the
  same format (the data is packed using python ``struct`` module).

* ``marisa_trie.BytesTrie`` - read-only Trie that maps unicode
  keys to lists of ``bytes`` objects.


marisa_trie.Trie
----------------

Create a new trie::

    >>> import marisa_trie
    >>> trie = marisa_trie.Trie([u'key1', u'key2', u'key12'])

Check if key is in trie::

    >>> u'key1' in trie
    True
    >>> u'key20' in trie
    False

Each key is assigned an unique ID from 0 to (n - 1), where n is the
number of keys::

    >>> trie.key_id(u'key2')
    1
    >>> trie[u'key2']  # alternative syntax
    1

Note that you can't assign a value to a ``marisa_trie.Trie`` key,
but can use the returned ID to store a value in a separate data structure
(e.g. in a python list or numpy array).

Key can be reconstructed from the ID::

    >>> trie.restore_key(1)
    u'key2'

Find all prefixes of a given key::

    >>> trie.prefixes(u'key12')
    [u'key1', u'key12']

There is also a generator version of ``.prefixes`` method
called ``.iter_prefixes``.

Find all keys from this trie that starts with a given prefix::

    >> trie.keys(u'key1')
    [u'key1', u'key12']

(iterator version ``.iterkeys(prefix)`` is also available).

Use ``items()`` method to return all (key, ID) pairs::

    >>> trie.items()
    [(u'key1', 0), (u'key12', 2), (u'key2', 1)]

Filter them by prefix::

    >>> trie.items(u'key1')
    [(u'key1', 0), (u'key12', 2)]

(iterator version ``.iteritems(prefix)`` is also available).

marisa_trie.RecordTrie
----------------------

Create a new trie::

    >>> keys = [u'foo', u'bar', u'foobar', u'foo']
    >>> values = [(1, 2), (2, 1), (3, 3), (2, 1)]
    >>> fmt = "<HH"   # a tuple with 2 short integers
    >>> trie = marisa_trie.RecordTrie(fmt, zip(keys, values))

Trie initial data must be an iterable of tuples ``(unicode_key, data_tuple)``.
Data tuples will be converted to bytes with ``struct.pack(fmt, *data_tuple)``.

Take a look at http://docs.python.org/library/struct.html#format-strings
for the format string specification.

Duplicate keys are allowed.

Check if key is in trie::

    >>> u'foo' in trie
    True
    >>> u'spam' in trie
    False

Get a values list::

    >>> trie[u'bar']
    [(2, 1)]
    >>> trie[u'foo']
    [(1, 2), (2, 1)]
    >>> trie.get(u'bar', 123)
    [(2, 1)]
    >>> trie.get(u'BAAR', 123) # default value
    123


Find all prefixes of a given key::

    >>> trie.prefixes(u'foobarz')
    [u'foo', u'foobar']

Test whether some key begins with a given prefix::

    >>> trie.has_keys_with_prefix(u'fo')
    True
    >>> trie.has_keys_with_prefix(u'go')
    False

Find all keys from this trie that starts with a given prefix::

    >> trie.keys(u'fo')
    [u'foo', u'foo', u'foobar']

Find all items from this trie that starts with a given prefix::

    >> trie.items(u'fo')
    [(u'foo', (1, 2)), (u'foo', (2, 1), (u'foobar', (3, 3))]


.. note::

    Iterator version of ``.keys()`` and ``.items()`` are not implemented yet.

marisa_trie.BytesTrie
---------------------

``BytesTrie`` is similar to ``RecordTrie``, but the values are raw bytes,
not tuples::

    >>> keys = [u'foo', u'bar', u'foobar', u'foo']
    >>> values = [b'foo-value', b'bar-value', b'foobar-value', b'foo-value2']
    >>> trie = marisa_trie.BytesTrie(zip(keys, values))
    >>> trie[u'bar']
    [b'bar-value']


Persistence
-----------

Trie objects supports saving/loading, pickling/unpickling
and memory mapped I/O.

Write trie to a stream::

    >>> with open('my_trie.marisa', 'w') as f:
    ...     trie.write(f)

Save trie to a file::

    >>> trie.save('my_trie_copy.marisa')

Read trie from stream::

    >>> trie2 = marisa_trie.Trie()
    >>> with open('my_trie.marisa', 'r') as f:
    ...     trie.read(f)


Load trie from file::

    >>> trie2.load('my_trie.marisa')

Trie objects are picklable::

    >>> import pickle
    >>> data = pickle.dumps(trie)
    >>> trie3 = pickle.loads(data)

You may also build a trie using ``marisa-build`` command-line
utility (provided by underlying C++ library; it should be downloaded and
compiled separately) and then load the trie from the resulting file
using ``.load()`` method.

Memory mapped I/O
-----------------

It is possible to use memory mapped file as data source::

    >>> trie = marisa_trie.RecordTrie(fmt).mmap('my_record_trie.marisa')

This way the whole dictionary won't be loaded to memory; memory
mapped I/O is an easy way to share dictionary data among processes.

.. warning::

    Memory mapped trie might cause a lot of random disk accesses which
    considerably increase the search time.

Trie storage options
--------------------

`marisa-trie`_ C++ library provides some configuration options for trie storage;
check http://marisa-trie.googlecode.com/svn/trunk/docs/readme.en.html page
(scroll down to "Enumeration Constants" section) to get an idea.

These options are exposed as ``order``, ``num_tries``, ``cache_size``
and ``binary`` keyword arguments for trie constructors.

For example, set ``order`` to ``marisa_trie.LABEL_ORDER`` in order to
make trie functions return results in alphabetical oder::

    >>> trie = marisa_trie.RecordTrie(fmt, data, order=marisa_trie.LABEL_ORDER)

Note that two tries constructed from identical data but with different ``order``
arguments will compare unequal::

    >>> t1 = marisa_trie.Trie(order=marisa_trie.LABEL_ORDER)
    >>> t2 = marisa_trie.Trie(order=marisa_trie.WEIGHT_ORDER)
    >>> t1 == t2
    False


Benchmarks
==========

My quick tests show that memory usage is quite decent.
For a list of 3000000 (3 million) Russian words memory consumption
with different data structures (under Python 2.7):

* dict(unicode words -> word lenghts): about 600M
* list(unicode words) : about 300M
* BaseTrie from datrie_ library: about 70M
* ``marisa_trie.RecordTrie`` : 11M
* ``marisa_trie.Trie``: 7M


.. note::

    Lengths of words were stored as values in ``datrie.BaseTrie``
    and ``marisa_trie.RecordTrie``. ``RecordTrie`` compresses
    similar values and the key compression is better so it uses
    much less memory than ``datrie.BaseTrie``.

    ``marisa_trie.Trie`` provides auto-assigned IDs. It is not possible
    to store arbitrary values in ``marisa_trie.Trie`` so it uses less
    memory than ``RecordTrie``.

Benchmark results (100k unicode words, integer values (lenghts of the words),
Python 3.2, macbook air i5 1.8 Ghz)::

    dict building                     2.919M words/sec
    Trie building                     0.394M words/sec
    BytesTrie building                0.355M words/sec
    RecordTrie building               0.354M words/sec

    dict __getitem__ (hits)           8.239M ops/sec
    Trie __getitem__ (hits)           not supported
    BytesTrie __getitem__ (hits)      0.498M ops/sec
    RecordTrie __getitem__ (hits)     0.404M ops/sec

    dict get() (hits)                 4.410M ops/sec
    Trie get() (hits)                 not supported
    BytesTrie get() (hits)            0.458M ops/sec
    RecordTrie get() (hits)           0.364M ops/sec
    dict get() (misses)               4.869M ops/sec
    Trie get() (misses)               not supported
    BytesTrie get() (misses)          0.849M ops/sec
    RecordTrie get() (misses)         0.816M ops/sec

    dict __contains__ (hits)          8.053M ops/sec
    Trie __contains__ (hits)          1.018M ops/sec
    BytesTrie __contains__ (hits)     0.605M ops/sec
    RecordTrie __contains__ (hits)    0.618M ops/sec
    dict __contains__ (misses)        6.489M ops/sec
    Trie __contains__ (misses)        2.047M ops/sec
    BytesTrie __contains__ (misses)   1.079M ops/sec
    RecordTrie __contains__ (misses)  1.123M ops/sec

    dict items()                      57.248 ops/sec
    Trie items()                      not supported
    BytesTrie items()                 11.691 ops/sec
    RecordTrie items()                8.369 ops/sec

    dict keys()                       217.920 ops/sec
    Trie keys()                       19.589 ops/sec
    BytesTrie keys()                  14.849 ops/sec
    RecordTrie keys()                 15.369 ops/sec

    Trie.prefixes (hits)              0.594M ops/sec
    Trie.prefixes (mixed)             1.874M ops/sec
    Trie.prefixes (misses)            1.447M ops/sec
    RecordTrie.prefixes (hits)        0.103M ops/sec
    RecordTrie.prefixes (mixed)       0.458M ops/sec
    RecordTrie.prefixes (misses)      0.164M ops/sec
    Trie.iter_prefixes (hits)         0.588M ops/sec
    Trie.iter_prefixes (mixed)        1.470M ops/sec
    Trie.iter_prefixes (misses)       1.170M ops/sec

    Trie.keys(prefix="xxx"), avg_len(res)==415                   5.044K ops/sec
    Trie.keys(prefix="xxxxx"), avg_len(res)==17                  89.363K ops/sec
    Trie.keys(prefix="xxxxxxxx"), avg_len(res)==3                258.732K ops/sec
    Trie.keys(prefix="xxxxx..xx"), avg_len(res)==1.4             293.199K ops/sec
    Trie.keys(prefix="xxx"), NON_EXISTING                        1169.524K ops/sec

    RecordTrie.keys(prefix="xxx"), avg_len(res)==415             3.836K ops/sec
    RecordTrie.keys(prefix="xxxxx"), avg_len(res)==17            73.591K ops/sec
    RecordTrie.keys(prefix="xxxxxxxx"), avg_len(res)==3          229.515K ops/sec
    RecordTrie.keys(prefix="xxxxx..xx"), avg_len(res)==1.4       269.228K ops/sec
    RecordTrie.keys(prefix="xxx"), NON_EXISTING                  1071.433K ops/sec


Tries from ``marisa_trie`` are static and uses less memory, tries from
`datrie`_ are faster and can be updated.

You may also give DAWG_ a try - it is usually faster than
``marisa-trie`` and sometimes can use less memory (depending on data).

Please take this benchmark results with a grain of salt; this
is a very simple benchmark on a single data set.

.. _datrie: https://github.com/kmike/datrie
.. _DAWG: https://github.com/kmike/DAWG

Current limitations
===================

* The library is not tested with mingw32 compiler;
* ``.prefixes()`` method of ``BytesTrie`` and ``RecordTrie`` is quite slow
  and doesn't have iterator counterpart;
* ``read()`` and ``write()`` methods don't work with file-like objects
  (they work only with real files; pickling works fine for file-like objects);
* there are ``keys()`` and ``items()`` methods but no ``values()`` method.

Contributions are welcome!

Contributing
============

Development happens at github: https://github.com/kmike/marisa-trie

Feel free to submit ideas, bug reports and pull requests.

If you found a bug in a C++ part please report it to the original
`bug tracker <https://code.google.com/p/marisa-trie/issues/list>`_.

How is source code organized
----------------------------

There are 4 folders in repository:

* ``bench`` - benchmarks & benchmark data;
* ``lib`` - original unmodified `marisa-trie`_ C++ library which is bundled
  for easier distribution; if something is have to be fixed in this library
  consider fixing it in the `original repo <https://code.google.com/p/marisa-trie/>`_ ;
* ``src`` - wrapper code; ``src/marisa_trie.pyx`` is a wrapper implementation;
  ``src/*.pxd`` files are Cython headers for corresponding C++ headers;
  ``src/*.cpp`` files are the pre-built extension code and shouldn't be
  modified directly (they should be updated via ``update_cpp.sh`` script).
* ``tests`` - the test suite.


Running tests and benchmarks
----------------------------

Make sure `tox`_ is installed and run

::

    $ tox

from the source checkout. Tests should pass under python 2.6, 2.7,
3.2, 3.3 and 3.4.

In order to run benchmarks, type

::

    $ tox -c bench.ini


.. _cython: http://cython.org
.. _tox: http://tox.testrun.org

Authors & Contributors
----------------------

* Mikhail Korobov <kmike84@gmail.com>
* `Matt Hickford <https://github.com/matt-hickford>`_
* Sergei Lebedev <superbobry@gmail.com>

This module is based on `marisa-trie`_ C++ library by
Susumu Yata & contributors.

License
=======

Wrapper code is licensed under MIT License.
Bundled `marisa-trie`_ C++ library is dual-licensed under
LGPL and BSD 2-clause license.
