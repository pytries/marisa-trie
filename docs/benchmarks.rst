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
