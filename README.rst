marisa-trie
===========

MARISA-Trie structure for Python (2.x and 3.x).
Uses `marisa-trie`_ C++ library.

MARISA-Trie is a static trie that is very memory efficient and fairly fast.

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

Create a new trie::

    >>> import marisa_trie
    >>> trie = marisa_trie.Trie()

Build a trie::

    >>> trie.build([u'key1', u'key2', u'key12'])
    <marisa_trie.Trie at ...>

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

.. note::

    In future versions dict-like interface may become builtin.


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

It is possible to save a trie to a file::

    >>> with open('my_trie.marisa', 'w') as f:
    ...     trie.write(f)

or::

    >>> trie.save('my_trie_copy.marisa')

Load a trie::

    >>> trie2 = marisa.Trie()
    >>> with open('my_trie.marisa', 'r') as f:
    ...     trie.load(f)

or::

    >>> trie2.load('my_trie.marisa')

Trie objects are picklable::

    >>> import pickle
    >>> data = pickle.dumps(trie)
    >>> trie3 = pickle.loads(data)

You could also build a trie using ``marisa-build`` command-line
utility (provided by underlying C library; it should be downloaded and
compiled separately) and then load it from resulting file using ``.load()``
method.

Benchmarks
==========

My quick tests show that memory usage is quite decent.
For a list of 3000000 (3 million) Russian words memory consumption
with different data structures (under Python 2.7):

* list(unicode words) : about 300M
* BaseTrie from datrie_ library: about 70M
* marisa_trie.Trie: 7M

.. note::

    This is not a fair comparison because ``datrie.BaseTrie`` is able to
    store arbitrary integers as values and ``marisa_trie.Trie`` uses
    auto-assigned IDs.

Some speed data for ``marisa_trie.Trie`` (100k unicode words, Python 3.2,
macbook air i5 1.8 Ghz)::

    dict __contains__ (hits):       4.147M ops/sec
    trie __contains__ (hits):       0.887M ops/sec
    dict __contains__ (misses):     3.234M ops/sec
    trie __contains__ (misses):     1.529M ops/sec
    dict __len__:                   599186.286 ops/sec
    trie __len__:                   433893.517 ops/sec
    dict keys():                    215.424 ops/sec
    trie keys():                    3.425 ops/sec
    trie.iter_prefixes (hits):      0.169M ops/sec
    trie.iter_prefixes (misses):    0.822M ops/sec
    trie.iter_prefixes (mixed):     0.747M ops/sec

    trie.keys(prefix="xxx"), avg_len(res)==415:         0.840K ops/sec
    trie.keys(prefix="xxxxx"), avg_len(res)==17:        19.172K ops/sec
    trie.keys(prefix="xxxxxxxx"), avg_len(res)==3:      82.777K ops/sec
    trie.keys(prefix="xxxxx..xx"), avg_len(res)==1.4:   131.348K ops/sec
    trie.keys(prefix="xxx"), NON_EXISTING:              1027.093K ops/sec

So ``marisa_trie.Trie`` uses less memory, ``datrie.Trie`` is faster.

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

::

    $ tox -c bench.ini

runs benchmarks.

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
./