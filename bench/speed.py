#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, division

import gzip
import os
import random
import string
import struct
import timeit

import marisa_trie


def words100k():
    zip_name = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "words100k.txt.gz"
    )

    return list(map(str.rstrip, gzip.open(zip_name, "rt")))


def random_words(num):
    russian = "абвгдеёжзиклмнопрстуфхцчъыьэюя"
    alphabet = "%s%s" % (russian, string.ascii_letters)
    return [
        "".join(random.choice(alphabet) for x in range(random.randint(1, 15)))
        for y in range(num)
    ]


def truncated_words(words):
    return [word[:3] for word in words]


def prefixes1k(words, prefix_len):
    words = [w for w in words if len(w) >= prefix_len]
    every_nth = int(len(words) / 1000)
    _words = [w[:prefix_len] for w in words[::every_nth]]
    return _words[:1000]


WORDS100k = words100k()
MIXED_WORDS100k = truncated_words(WORDS100k)
NON_WORDS100k = random_words(100000)
PREFIXES_3_1k = prefixes1k(WORDS100k, 3)
PREFIXES_5_1k = prefixes1k(WORDS100k, 5)
PREFIXES_8_1k = prefixes1k(WORDS100k, 8)
PREFIXES_15_1k = prefixes1k(WORDS100k, 15)


def format_result(key, value, text_width):
    key = key.ljust(text_width)
    print("    %s %s" % (key, value))


def bench(
    name, timer, descr="M ops/sec", op_count=0.1, repeats=3, runs=5, text_width=33
):
    try:
        times = []
        for x in range(runs):
            times.append(timer.timeit(repeats))

        def op_time(time):
            return op_count * repeats / time

        val = "%0.3f%s" % (op_time(min(times)), descr)
        format_result(name, val, text_width)
    except (AttributeError, TypeError):
        format_result(name, "not supported", text_width)


def create_trie():
    words = WORDS100k
    return marisa_trie.Trie(words)


def create_bytes_trie():
    words = WORDS100k
    values = (struct.pack("<H", len(word)) for word in words)
    return marisa_trie.BytesTrie(zip(words, values))


def create_record_trie():
    words = WORDS100k
    values = ([len(word)] for word in words)
    return marisa_trie.RecordTrie("<H", zip(words, values))


def benchmark():
    print("\n====== Benchmarks (100k unique unicode words) =======\n")

    common_setup = """
from __main__ import create_trie, create_bytes_trie, create_record_trie
from __main__ import WORDS100k, NON_WORDS100k, MIXED_WORDS100k
from __main__ import PREFIXES_3_1k, PREFIXES_5_1k, PREFIXES_8_1k, PREFIXES_15_1k
NON_WORDS_10k = NON_WORDS100k[:10000]
NON_WORDS_1k = ['ыва', 'xyz', 'соы', 'Axx', 'avы']*200
"""
    BUILD = {
        "dict": "data = dict((word, len(word)) for word in WORDS100k);",
        "Trie": "data = create_trie();",
        "BytesTrie": "data = create_bytes_trie();",
        "RecordTrie": "data = create_record_trie();",
    }

    dict_setup = common_setup + BUILD["dict"]
    trie_setup = common_setup + BUILD["Trie"]
    bytes_trie_setup = common_setup + BUILD["BytesTrie"]
    record_trie_setup = common_setup + BUILD["RecordTrie"]

    structures = [
        ("dict", dict_setup),
        ("Trie", trie_setup),
        ("BytesTrie", bytes_trie_setup),
        ("RecordTrie", record_trie_setup),
    ]

    # build performance
    for name, setup in structures:
        timer = timeit.Timer(BUILD[name], common_setup)
        bench("%s building" % name, timer, "M words/sec", 0.1, 5)

    # common operations speed
    tests = [
        (
            "__getitem__ (hits)",
            "for word in WORDS100k: data[word]",
            "M ops/sec",
            0.1,
            3,
        ),
        ("get() (hits)", "for word in WORDS100k: data.get(word)", "M ops/sec", 0.1, 3),
        (
            "get() (misses)",
            "for word in NON_WORDS_10k: data.get(word)",
            "M ops/sec",
            0.01,
            5,
        ),
        (
            "__contains__ (hits)",
            "for word in WORDS100k: word in data",
            "M ops/sec",
            0.1,
            3,
        ),
        (
            "__contains__ (misses)",
            "for word in NON_WORDS100k: word in data",
            "M ops/sec",
            0.1,
            3,
        ),
        ("items()", "list(data.items())", " ops/sec", 1, 1),
        ("keys()", "list(data.keys())", " ops/sec", 1, 1),
        #        ('values()', 'list(data.values())', ' ops/sec', 1, 1),
    ]

    for test_name, test, descr, op_count, repeats in tests:
        for name, setup in structures:
            timer = timeit.Timer(test, setup)
            full_test_name = "%s %s" % (name, test_name)
            bench(full_test_name, timer, descr, op_count, repeats, 9)

    # trie-specific benchmarks
    for struct_name, setup in structures[1:]:
        _bench_data = [
            ("hits", "WORDS100k"),
            ("mixed", "MIXED_WORDS100k"),
            ("misses", "NON_WORDS100k"),
        ]

        for meth in ["prefixes", "iter_prefixes"]:
            for name, data in _bench_data:
                bench(
                    "%s.%s (%s)" % (struct_name, meth, name),
                    timeit.Timer(
                        "for word in %s:\n"
                        "   for it in data.%s(word): pass" % (data, meth),
                        setup,
                    ),
                    runs=3,
                )

        _bench_data = [
            ("xxx", "avg_len(res)==415", "PREFIXES_3_1k"),
            ("xxxxx", "avg_len(res)==17", "PREFIXES_5_1k"),
            ("xxxxxxxx", "avg_len(res)==3", "PREFIXES_8_1k"),
            ("xxxxx..xx", "avg_len(res)==1.4", "PREFIXES_15_1k"),
            ("xxx", "NON_EXISTING", "NON_WORDS_1k"),
        ]
        for xxx, avg, data in _bench_data:
            for meth in ["keys"]:  # ('items', 'keys', 'values'):
                bench(
                    '%s.%s(prefix="%s"), %s' % (struct_name, meth, xxx, avg),
                    timeit.Timer("for word in %s: data.%s(word)" % (data, meth), setup),
                    "K ops/sec",
                    op_count=1,
                    runs=3,
                    text_width=60,
                )


def check_trie(trie, words):
    assert sum(trie[word] for word in words) == len(words)


def profiling():
    import pstats
    import cProfile

    print("\n====== Profiling =======\n")
    trie = create_trie()
    WORDS = WORDS100k

    #    def check_prefixes(trie, words):
    #        for word in words:
    #            trie.keys(word)
    #    cProfile.runctx("check_prefixes(trie, NON_WORDS_1k)", globals(), locals(), "Profile.prof")
    #
    cProfile.runctx("check_trie(trie, WORDS)", globals(), locals(), "Profile.prof")

    s = pstats.Stats("Profile.prof")
    s.strip_dirs().sort_stats("time").print_stats(20)


if __name__ == "__main__":
    benchmark()
    # profiling()
    print("\n~~~~~~~~~~~~~~\n")
