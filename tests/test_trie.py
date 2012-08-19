# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import string
import random
import tempfile
import pickle

import pytest

import marisa_trie

def get_random_words(count):
    russian = 'абвгдеёжзиклмнопрстуфхцчъыьэюя'
    alphabet = russian + string.ascii_lowercase

    def random_word(length):
        return "".join([random.choice(alphabet) for x in range(random.randint(1,length))])

    return list(set(random_word(10) for y in range(count)))


def test_build():
    trie = marisa_trie.Trie()
    keys = get_random_words(1000)

    trie.build(keys)

    for key in keys:
        assert key in trie

    non_key = '2135'
    assert non_key not in trie


def test_contains():
    trie = marisa_trie.Trie()
    assert 'foo' not in trie

    trie.build(['foo'])
    assert 'foo' in trie
    assert 'f' not in trie

def test_key_id():
    words = ['foo', 'bar', 'f']
    trie = marisa_trie.Trie().build(words)
    for word in words:
        key_id = trie.key_id(word)
        assert trie.restore_key(key_id) == word


    key_ids = [trie.key_id(word) for word in words]
    non_existing_id = max(key_ids) + 1

    with pytest.raises(KeyError):
        trie.restore_key(non_existing_id)

    with pytest.raises(KeyError):
        print(trie.key_id('fo'))

def test_saveload():
    fd, fname = tempfile.mkstemp()

    words = ['foo', 'bar', 'f']
    trie = marisa_trie.Trie().build(words)

    with open(fname, 'w') as f:
        trie.write(f)

    with open(fname, 'r') as f:
        trie2 = marisa_trie.Trie()
        trie2.read(f)

    for word in words:
        assert word in trie2


def test_mmap():
    fd, fname = tempfile.mkstemp()
    words = get_random_words(1000)
    trie = marisa_trie.Trie().build(words)
    with open(fname, 'w') as f:
        trie.write(f)

    trie2 = marisa_trie.Trie()
    trie2.mmap(fname)

    for word in words:
        assert word in trie2

def test_dumps_loads():
    words = get_random_words(1000)
    trie = marisa_trie.Trie().build(words)
    data = trie.dumps()

    trie2 = marisa_trie.Trie()
    trie2.loads(data)

    for word in words:
        assert word in trie2
        assert trie2.key_id(word) == trie.key_id(word)

def test_pickling():
    words = get_random_words(1000)
    trie = marisa_trie.Trie().build(words)

    data = pickle.dumps(trie)
    trie2 = pickle.loads(data)

    for word in words:
        assert word in trie2
        assert trie2.key_id(word) == trie.key_id(word)


def test_len():
    trie = marisa_trie.Trie()
    assert len(trie) == 0

    trie.build(['foo', 'f', 'bar'])
    assert len(trie) == 3

def test_prefixes():
    trie = marisa_trie.Trie().build(['foo', 'f', 'foobar', 'bar'])
    assert trie.prefixes('foobar') == ['f', 'foo', 'foobar']
    assert trie.prefixes('foo') == ['f', 'foo']
    assert trie.prefixes('bar') == ['bar']
    assert trie.prefixes('b') == []

    assert list(trie.iter_prefixes('foobar')) == ['f', 'foo', 'foobar']

def test_keys():
    keys = ['foo', 'f', 'foobar', 'bar']
    trie = marisa_trie.Trie().build(keys)
    assert set(trie.keys()) == set(keys)

def test_keys_prefix():
    keys = ['foo', 'f', 'foobar', 'bar']
    trie = marisa_trie.Trie().build(keys)
    assert set(trie.keys('fo')) == set(['foo', 'foobar'])
    assert trie.keys('foobarz') == []