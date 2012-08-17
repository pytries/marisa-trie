# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import string
import random
import tempfile

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