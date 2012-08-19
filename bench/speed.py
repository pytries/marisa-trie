#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import random
import string
import timeit
import os
import zipfile
#import pstats
#import cProfile

import marisa_trie

def words100k():
    zip_name = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'words100k.txt.zip'
    )
    zf = zipfile.ZipFile(zip_name)
    txt = zf.open(zf.namelist()[0]).read().decode('utf8')
    return txt.splitlines()

def random_words(num):
    russian = 'абвгдеёжзиклмнопрстуфхцчъыьэюя'
    alphabet = russian + string.ascii_letters
    return [
        "".join([random.choice(alphabet) for x in range(random.randint(1,15))])
        for y in range(num)
    ]

def truncated_words(words):
    return [word[:3] for word in words]

def prefixes1k(words, prefix_len):
    words = [w for w in words if len(w) >= prefix_len]
    every_nth = int(len(words)/1000)
    _words = [w[:prefix_len] for w in words[::every_nth]]
    return _words[:1000]

WORDS100k = words100k()
MIXED_WORDS100k = truncated_words(WORDS100k)
NON_WORDS100k = random_words(100000)
PREFIXES_3_1k = prefixes1k(WORDS100k, 3)
PREFIXES_5_1k = prefixes1k(WORDS100k, 5)
PREFIXES_8_1k = prefixes1k(WORDS100k, 8)
PREFIXES_15_1k = prefixes1k(WORDS100k, 15)


def bench(name, timer, descr='M ops/sec', op_count=0.1, repeats=3, runs=5):
    times = []
    for x in range(runs):
        times.append(timer.timeit(repeats))

    def op_time(time):
        return op_count*repeats / time

    print("%55s:    %0.3f%s" % (
        name,
        op_time(min(times)),
        descr,
    ))

def create_trie():
    words = words100k()
    trie = marisa_trie.Trie()
    trie.build(words)
    return trie

def benchmark():
    print('\n====== Benchmarks (100k unique unicode words) =======\n')

    tests = [
        #('__getitem__ (hits)', "for word in words: data[word]", 'M ops/sec', 0.1, 3),
        ('__contains__ (hits)', "for word in words: word in data", 'M ops/sec', 0.1, 3),
        ('__contains__ (misses)', "for word in NON_WORDS100k: word in data", 'M ops/sec', 0.1, 3),
        ('__len__', 'len(data)', ' ops/sec', 1, 3),
        #('__setitem__ (updates)', 'for word in words: data[word]=1', 'M ops/sec',0.1, 3),
        #('__setitem__ (inserts)', 'for word in NON_WORDS_10k: data[word]=1', 'M ops/sec',0.01, 3),
        #('setdefault (updates)', 'for word in words: data.setdefault(word, 1)', 'M ops/sec', 0.1, 3),
        #('setdefault (inserts)', 'for word in  NON_WORDS_10k: data.setdefault(word, 1)', 'M ops/sec', 0.01, 3),
#        ('items()', 'list(data.items())', ' ops/sec', 1, 1),
        ('keys()', 'list(data.keys())', ' ops/sec', 1, 1),
#        ('values()', 'list(data.values())', ' ops/sec', 1, 1),
    ]

    common_setup = """
from __main__ import create_trie, WORDS100k, NON_WORDS100k, MIXED_WORDS100k
from __main__ import PREFIXES_3_1k, PREFIXES_5_1k, PREFIXES_8_1k, PREFIXES_15_1k
words = WORDS100k
NON_WORDS_10k = NON_WORDS100k[:10000]
NON_WORDS_1k = ['ыва', 'xyz', 'соы', 'Axx', 'avы']*200
"""
    dict_setup = common_setup + 'data = dict((word, 1) for word in words);'
    trie_setup = common_setup + 'data = create_trie();'

    for test_name, test, descr, op_count, repeats in tests:
        t_dict = timeit.Timer(test, dict_setup)
        t_trie = timeit.Timer(test, trie_setup)

        bench('dict '+test_name, t_dict, descr, op_count, repeats)
        bench('trie '+test_name, t_trie, descr, op_count, repeats)


    # trie-specific benchmarks

#    bench(
#        'trie.iter_prefix_items (hits)',
#        timeit.Timer(
#            "for word in words:\n"
#            "   for it in data.iter_prefix_items(word):\n"
#            "       pass",
#            trie_setup
#        ),
#    )
#
#    bench(
#        'trie.prefix_items (hits)',
#        timeit.Timer(
#            "for word in words: data.prefix_items(word)",
#            trie_setup
#        )
#    )
#
#    bench(
#        'trie.prefix_items loop (hits)',
#        timeit.Timer(
#            "for word in words:\n"
#            "    for it in data.prefix_items(word):pass",
#            trie_setup
#        )
#    )
#
    bench(
        'trie.iter_prefixes (hits)',
        timeit.Timer(
            "for word in words:\n"
            "   for it in data.iter_prefixes(word): pass",
            trie_setup
        )
    )

    bench(
        'trie.iter_prefixes (misses)',
        timeit.Timer(
            "for word in NON_WORDS100k:\n"
            "   for it in data.iter_prefixes(word): pass",
            trie_setup
        )
    )

    bench(
        'trie.iter_prefixes (mixed)',
        timeit.Timer(
            "for word in MIXED_WORDS100k:\n"
            "   for it in data.iter_prefixes(word): pass",
            trie_setup
        )
    )

#    bench(
#        'trie.has_keys_with_prefix (hits)',
#        timeit.Timer(
#            "for word in words: data.has_keys_with_prefix(word)",
#            trie_setup
#        )
#    )
#
#    bench(
#        'trie.has_keys_with_prefix (misses)',
#        timeit.Timer(
#            "for word in NON_WORDS100k: data.has_keys_with_prefix(word)",
#            trie_setup
#        )
#    )
#
#    for meth in ('longest_prefix', 'longest_prefix_item'):
#        bench(
#            'trie.%s (hits)' % meth,
#            timeit.Timer(
#                "for word in words: data.%s(word)" % meth,
#                trie_setup
#            )
#        )
#
#        bench(
#            'trie.%s (misses)' % meth,
#            timeit.Timer(
#                "for word in NON_WORDS100k: data.%s(word, default=None)" % meth,
#                trie_setup
#            )
#        )
#
#        bench(
#            'trie.%s (mixed)' % meth,
#            timeit.Timer(
#                "for word in MIXED_WORDS100k: data.%s(word, default=None)" % meth,
#                trie_setup
#            )
#        )
#
#
    prefix_data = [
        ('xxx', 'avg_len(res)==415', 'PREFIXES_3_1k'),
        ('xxxxx', 'avg_len(res)==17', 'PREFIXES_5_1k'),
        ('xxxxxxxx', 'avg_len(res)==3', 'PREFIXES_8_1k'),
        ('xxxxx..xx', 'avg_len(res)==1.4', 'PREFIXES_15_1k'),
        ('xxx', 'NON_EXISTING', 'NON_WORDS_1k'),
    ]
    for xxx, avg, data in prefix_data:
        for meth in ['keys']: #('items', 'keys', 'values'):
            bench(
                'trie.%s(prefix="%s"), %s' % (meth, xxx, avg),
                timeit.Timer(
                    "for word in %s: data.%s(word)" % (data, meth),
                    trie_setup
                ),
                'K ops/sec',
                op_count=1,
            )

def check_trie(trie, words):
    value = 0
    for word in words:
        value += trie[word]
    if value != len(words):
        raise Exception()

def profiling():
    import pstats
    import cProfile
    print('\n====== Profiling =======\n')
    trie = create_trie()
    WORDS = words100k()

#    def check_prefixes(trie, words):
#        for word in words:
#            trie.keys(word)
#    cProfile.runctx("check_prefixes(trie, NON_WORDS_1k)", globals(), locals(), "Profile.prof")
#
    cProfile.runctx("check_trie(trie, WORDS)", globals(), locals(), "Profile.prof")

    s = pstats.Stats("Profile.prof")
    s.strip_dirs().sort_stats("time").print_stats(20)

#def memory():
#    gc.collect()
#    _memory = lambda: _get_memory(os.getpid())
#    initial_memory = _memory()
#    trie = create_trie()
#    gc.collect()
#    trie_memory = _memory()
#
#    del trie
#    gc.collect()
#    alphabet, words = words100k()
#    words_dict = dict((word, 1) for word in words)
#    del alphabet
#    del words
#    gc.collect()
#
#    dict_memory = _memory()
#    print('initial: %s, trie: +%s, dict: +%s' % (
#        initial_memory,
#        trie_memory-initial_memory,
#        dict_memory-initial_memory,
#    ))

if __name__ == '__main__':
#    trie = create_trie()
#    def check_pref(prefixes):
#        cntr = 0
#        for w in prefixes:
#            cntr += len(trie.keys(w))
#        print(len(prefixes), cntr, cntr / len(prefixes))
#    check_pref(prefixes1k(WORDS100k, 15))


    benchmark()
    #profiling()
    #memory()
    print('\n~~~~~~~~~~~~~~\n')