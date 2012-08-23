marisa-trie
===========

Static memory-efficient Trie structures for Python (2.x and 3.x).
Uses `marisa-trie`_ C++ library.

There are official SWIG-based Python bindings included
in C++ library distribution; this package provides an alternative
unofficial Cython-based pip-installable Python bindings.

.. _marisa-trie: https://code.google.com/p/marisa-trie/

Installation
============

::

    pip install marisa-trie

Usage
=====

There are several Trie classes in this package:

* ``marisa_trie.Trie`` - read-only trie-based data structure that maps
  unicode keys to auto-generated unique IDs and supports exact and prefix
  lookups;

* ``marisa_trie.RecordTrie`` - read-only trie-based data structure that
  maps unicode keys to lists of data tuples. All tuples must be of the
  same format (the data is packed with using python ``struct`` module).
  ``RecordTrie`` supports exact and prefix lookups.

* ``marisa_trie.BytesTrie`` - read-only Trie that maps unicode
  keys to lists of ``bytes`` objects.  ``BytesTrie`` supports exact
  and prefix lookups.


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
number of keys; you can use this ID to store a value in a
separate structure (e.g. python list)::

    >>> trie.key_id(u'key2')
    1

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

Find all prefixes of a given key::

    >>> trie.prefixes(u'foobarz')
    [u'foo', u'foobar']

Find all keys from this trie that starts with a given prefix::

    >> trie.keys(u'fo')
    [u'foo', u'foo', u'foobar']

Find all items from this trie that starts with a given prefix::

    >> trie.items(u'fo')
    [(u'foo', (1, 2)), (u'foo', (2, 1), (u'foobar', (3, 3))]


.. note::

    Iterator version of ``.keys()`` and ``.items()`` are not implemented yet.


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

    >>> trie = marisa_trie.RecordTrie(fmt)
    >>> trie.mmap('my_record_trie.marisa')

This way the whole dictionary won't be loaded to memory; memory
mapped I/O is an easy way to share dictionary data among processes.

.. warning::

    Memory mapped trie might cause a lot of random disk accesses which
    considerably increase the search time.


Benchmarks
==========

My quick tests show that memory usage is quite decent.
For a list of 3000000 (3 million) Russian words memory consumption
with different data structures (under Python 2.7):

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

    dict __getitem__ (hits):            4.090M ops/sec
    Trie __getitem__ (hits):            not supported
    BytesTrie __getitem__ (hits):       0.469M ops/sec
    RecordTrie __getitem__ (hits):      0.373M ops/sec
    dict __contains__ (hits):           4.036M ops/sec
    Trie __contains__ (hits):           0.910M ops/sec
    BytesTrie __contains__ (hits):      0.573M ops/sec
    RecordTrie __contains__ (hits):     0.591M ops/sec
    dict __contains__ (misses):         3.346M ops/sec
    Trie __contains__ (misses):         1.643M ops/sec
    BytesTrie __contains__ (misses):    0.976M ops/sec
    RecordTrie __contains__ (misses):   1.017M ops/sec
    dict items():                       58.316 ops/sec
    Trie items():                       not supported
    BytesTrie items():                  2.456 ops/sec
    RecordTrie items():                 2.254 ops/sec
    dict keys():                        211.194 ops/sec
    Trie keys():                        3.341 ops/sec
    BytesTrie keys():                   2.308 ops/sec
    RecordTrie keys():                  2.184 ops/sec
    Trie.prefixes (hits):               0.176M ops/sec
    Trie.prefixes (mixed):              0.956M ops/sec
    Trie.prefixes (misses):             1.035M ops/sec
    RecordTrie.prefixes (hits):         0.106M ops/sec
    RecordTrie.prefixes (mixed):        0.451M ops/sec
    RecordTrie.prefixes (misses):       0.173M ops/sec
    Trie.iter_prefixes (hits):          0.170M ops/sec
    Trie.iter_prefixes (mixed):         0.799M ops/sec
    Trie.iter_prefixes (misses):        0.898M ops/sec
    Trie.keys(prefix="xxx"), avg_len(res)==415:         0.825K ops/sec
    Trie.keys(prefix="xxxxx"), avg_len(res)==17:        19.934K ops/sec
    Trie.keys(prefix="xxxxxxxx"), avg_len(res)==3:      85.239K ops/sec
    Trie.keys(prefix="xxxxx..xx"), avg_len(res)==1.4:   136.476K ops/sec
    Trie.keys(prefix="xxx"), NON_EXISTING:              1073.719K ops/sec


Tries from ``marisa_trie`` uses less memory, tries from
``datrie.Trie`` are faster.

Please take this benchmark results with a grain of salt; this
is a very simple benchmark on a single data set.

.. _datrie: https://github.com/kmike/datrie

Contributing
============

Development happens at github and bitbucket:

* https://github.com/kmike/marisa-trie
* https://bitbucket.org/kmike/marisa-trie

The main issue tracker is at github: https://github.com/kmike/marisa-trie/issues

Feel free to submit ideas, bugs, pull requests (git or hg) or
regular patches.

If you found a bug in a C++ part please report it to the original
`bug tracker <https://code.google.com/p/marisa-trie/issues/list>`_.


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

In order to run benchmarks, type

::

    $ tox -c bench.ini


.. _cython: http://cython.org
.. _tox: http://tox.testrun.org

Authors & Contributors
----------------------

* Mikhail Korobov <kmike84@gmail.com>

This module is based on `marisa-trie`_ C++ library by
Susumu Yata & contributors.

License
=======

Wrapper code is licensed under MIT License.
Bundled `marisa-trie`_ C++ library is licensed under BSD license.
