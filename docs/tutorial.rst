.. _tutorial:

Tutorial
========

Tries
-----

There are several trie classes in this package:

.. autosummary::
   :nosignatures:

   marisa_trie.BinaryTrie
   marisa_trie.Trie
   marisa_trie.RecordTrie
   marisa_trie.BytesTrie

marisa_trie.Trie
~~~~~~~~~~~~~~~~

Create a new trie from a list of keys::

    >>> import marisa_trie
    >>> trie = marisa_trie.Trie(["key1", "key2", "key12"])

Check if a key is present::

    >>> "key1" in trie
    True
    >>> "key20" in trie
    False

Each key is assigned an unique ID from 0 to (n - 1), where n is the
number of keys in a trie::

    >>> trie["key2"]
    1

Note that you can't assign a value to a ``marisa_trie.Trie`` key,
but can use the returned ID to store values in a separate data structure
(e.g. in a Python list or NumPy array).

An ID can be mapped back to the corresponding key:

    >>> trie.restore_key(1)
    "key2"

Query a trie

* Find all trie keys which are prefixes of a given key::

      >>> trie.prefixes("key12")
      ["key1", "key12"]

* Find all trie keys which start with a given prefix::

      >> trie.keys("key1")
      ["key1", "key12"]

* The latter is complemented by :meth:`~marisa_trie.Trie.items` which
  returns all matching ``(key, ID)`` pairs.

All query methods have generator-based versions prefixed with ``iter``.

.. note::

   If you're looking for a trie with bytes keys, check out
   :class:`~marisa_trie.BinaryTrie`.


marisa_trie.RecordTrie
~~~~~~~~~~~~~~~~~~~~~~

Create a new trie from a list of ``(key, data)`` pairs::

    >>> keys = ["foo", "bar", "foobar", "foo"]
    >>> values = [(1, 2), (2, 1), (3, 3), (2, 1)]
    >>> fmt = "<HH"   # two short integers.
    >>> trie = marisa_trie.RecordTrie(fmt, zip(keys, values))

Each data tuple would be converted to bytes using :func:`struct.pack`. Take a
look at available `format strings <https://docs.python.org/3/library/struct.html#format-strings>`_.

Check if a key is present::

    >>> "foo" in trie
    True
    >>> "spam" in trie
    False

``marisa_trie.RecordTrie`` allows duplicate keys. Therefore ``__getitem__`` and
``get`` return a list of values.

    >>> trie["bar"]
    [(2, 1)]
    >>> trie["foo"]
    [(1, 2), (2, 1)]
    >>> trie.get("bar", 123)
    [(2, 1)]
    >>> trie.get("BAAR", 123)  # default value.
    123

Similarly, :meth:`~marisa_trie.RecordTrie.keys` and
:meth:`~marisa_trie.RecordTrie.items` take into account key multiplicities::

    >> trie.keys("fo")
    ["foo", "foo", "foobar"]
    >> trie.items("fo")
    [("foo", (1, 2)), ("foo", (2, 1)), ("foobar", (3, 3))]


marisa_trie.BytesTrie
~~~~~~~~~~~~~~~~~~~~~

``BytesTrie`` is similar to ``RecordTrie``, but the values are raw bytes,
not tuples::

    >>> keys = ["foo", "bar", "foobar", "foo"]
    >>> values = [b'foo-value', b'bar-value', b'foobar-value', b'foo-value2']
    >>> trie = marisa_trie.BytesTrie(zip(keys, values))
    >>> trie["bar"]
    [b'bar-value']


Persistence
-----------

Trie objects supports saving/loading, pickling/unpickling and memory mapped I/O.

Save trie to a file::

    >>> trie.save('my_trie.marisa')

Load trie from a file::

    >>> trie2 = marisa_trie.Trie()
    >>> trie2.load('my_trie.marisa')

.. note:: You may also build a trie using ``marisa-build`` command-line
          utility (provided by underlying C++ library; it should be
          downloaded and compiled separately) and then load the trie
          from the resulting file using ``load``.

Trie objects are picklable::

    >>> import pickle
    >>> data = pickle.dumps(trie)
    >>> trie3 = pickle.loads(data)


Memory mapped I/O
-----------------

It is possible to use memory mapped file as data source::

    >>> trie = marisa_trie.RecordTrie(fmt).mmap('my_record_trie.marisa')

This way the whole dictionary won't be loaded fully to memory; memory
mapped I/O is an easy way to share dictionary data among processes.

.. warning::

    Memory mapped trie might cause lots of random disk accesses which
    considerably increases the search time.


Storage options
---------------

`marisa-trie <https://github.com/s-yata/marisa-trie>`_ C++ library provides
some configuration options for trie storage; See "Enumeration Constants"
section in the library
`docs <http://s-yata.github.io/marisa-trie/docs/readme.en.html>`_.

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
