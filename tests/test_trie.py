# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import tempfile
import pickle

import pytest

import marisa_trie
from .utils import get_random_words


def test_build():
    keys = get_random_words(1000)
    trie = marisa_trie.Trie(keys)

    for key in keys:
        assert key in trie

    non_key = '2135'
    assert non_key not in trie


def test_contains():
    trie = marisa_trie.Trie()
    assert 'foo' not in trie

    trie = marisa_trie.Trie(['foo'])
    assert 'foo' in trie
    assert 'f' not in trie


def test_key_id():
    words = ['foo', 'bar', 'f']
    trie = marisa_trie.Trie(words)
    for word in words:
        key_id = trie.key_id(word)
        assert trie.restore_key(key_id) == word

    key_ids = [trie.key_id(word) for word in words]
    non_existing_id = max(key_ids) + 1

    with pytest.raises(KeyError):
        trie.restore_key(non_existing_id)

    with pytest.raises(KeyError):
        print(trie.key_id('fo'))


def test_getitem():
    words = ['foo', 'bar', 'f']
    trie = marisa_trie.Trie(words)
    for word in words:
        key_id = trie[word]
        assert trie.restore_key(key_id) == word

    key_ids = [trie[word] for word in words]
    non_existing_id = max(key_ids) + 1

    with pytest.raises(KeyError):
        trie.restore_key(non_existing_id)

    with pytest.raises(KeyError):
        print(trie['fo'])


def test_get():
    words = ['foo', 'bar', 'f']
    trie = marisa_trie.Trie(words)
    for word in words:
        key_id = trie.get(word)
        assert trie.restore_key(key_id) == word

        key_id = trie.get(word.encode('utf8'))
        assert trie.restore_key(key_id) == word

        key_id = trie.get(word, 'default value')
        assert trie.restore_key(key_id) == word

    assert trie.get('non_existing_key') is None
    assert trie.get(b'non_existing_bytes_key') is None
    assert trie.get('non_existing_key', 'default value') == 'default value'
    assert trie.get(b'non_existing_bytes_key', 'default value') == 'default value'


def test_saveload():
    fd, fname = tempfile.mkstemp()

    words = ['foo', 'bar', 'f']
    trie = marisa_trie.Trie(words)

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
    trie = marisa_trie.Trie(words)
    with open(fname, 'w') as f:
        trie.write(f)

    trie2 = marisa_trie.Trie()
    trie2.mmap(fname)

    for word in words:
        assert word in trie2


def test_dumps_loads():
    words = get_random_words(1000)
    trie = marisa_trie.Trie(words)
    data = trie.tobytes()

    trie2 = marisa_trie.Trie().frombytes(data)

    for word in words:
        assert word in trie2
        assert trie2.key_id(word) == trie.key_id(word)


def test_pickling():
    words = get_random_words(1000)
    trie = marisa_trie.Trie(words)

    data = pickle.dumps(trie)
    trie2 = pickle.loads(data)

    for word in words:
        assert word in trie2
        assert trie2.key_id(word) == trie.key_id(word)


def test_cmp():
    trie = marisa_trie.Trie()
    assert trie == trie
    assert trie == marisa_trie.Trie()

    trie = marisa_trie.Trie(["foo", "bar"])
    assert trie == marisa_trie.Trie(["foo", "bar"])
    assert trie != marisa_trie.Trie(["foo", "boo"])

    lo_trie = marisa_trie.Trie(order=marisa_trie.LABEL_ORDER)
    wo_trie = marisa_trie.Trie(order=marisa_trie.WEIGHT_ORDER)
    assert lo_trie == lo_trie and wo_trie == wo_trie
    assert lo_trie != wo_trie

    with pytest.raises(TypeError):
        marisa_trie.Trie() < marisa_trie.Trie()

    with pytest.raises(TypeError):
        marisa_trie.Trie() > marisa_trie.Trie()

    # not sure if it makes sense copy-pasting further.


def test_iter():
    trie = marisa_trie.Trie(["foo", "bar"])
    assert list(trie) == list(trie.iterkeys())


def test_len():
    trie = marisa_trie.Trie()
    assert len(trie) == 0

    trie = marisa_trie.Trie(['foo', 'f', 'bar'])
    assert len(trie) == 3


def test_prefixes():
    trie = marisa_trie.Trie(['foo', 'f', 'foobar', 'bar'])
    assert trie.prefixes('foobar') == ['f', 'foo', 'foobar']
    assert trie.prefixes('foo') == ['f', 'foo']
    assert trie.prefixes('bar') == ['bar']
    assert trie.prefixes('b') == []

    assert list(trie.iter_prefixes('foobar')) == ['f', 'foo', 'foobar']


def test_keys():
    keys = ['foo', 'f', 'foobar', 'bar']
    trie = marisa_trie.Trie(keys)
    assert set(trie.keys()) == set(keys)


def test_keys_prefix():
    keys = ['foo', 'f', 'foobar', 'bar']
    trie = marisa_trie.Trie(keys)
    assert set(trie.keys('fo')) == set(['foo', 'foobar'])
    assert trie.keys('foobarz') == []


def test_iterkeys():
    keys = get_random_words(1000)
    trie = marisa_trie.Trie(keys)
    assert trie.keys() == list(trie.iterkeys())

    for key in keys:
        prefix = key[:5]
        assert trie.keys(prefix) == list(trie.iterkeys(prefix))


def test_items():
    keys = ['foo', 'f', 'foobar', 'bar']
    trie = marisa_trie.Trie(keys)
    items = trie.items()
    assert set(items) == set(zip(keys, (trie[k] for k in keys)))


def test_items_prefix():
    keys = ['foo', 'f', 'foobar', 'bar']
    trie = marisa_trie.Trie(keys)
    assert set(trie.items('fo')) == set([
        ('foo', trie['foo']),
        ('foobar', trie['foobar']),
    ])


def test_iteritems():
    keys = get_random_words(1000)
    trie = marisa_trie.Trie(keys)
    assert trie.items() == list(trie.iteritems())

    for key in keys:
        prefix = key[:5]
        assert trie.items(prefix) == list(trie.iteritems(prefix))


def test_has_keys_with_prefix():
    empty_trie = marisa_trie.Trie()
    assert empty_trie.has_keys_with_prefix('') == False
    assert empty_trie.has_keys_with_prefix('ab') == False

    fruit_trie = marisa_trie.Trie(['apple', 'pear', 'peach'])
    assert fruit_trie.has_keys_with_prefix('') == True
    assert fruit_trie.has_keys_with_prefix('a') == True
    assert fruit_trie.has_keys_with_prefix('pe') == True
    assert fruit_trie.has_keys_with_prefix('pear') == True
    assert fruit_trie.has_keys_with_prefix('x') == False


def test_invalid_file():
    try:
        marisa_trie.Trie().load(__file__)
    except RuntimeError as e:
        assert "MARISA_FORMAT_ERROR" in e.args[0]
    else:
        raise AssertionError("Exception is not raised")


#def test_int_trie():
#    data = {'foo': 10, 'f': 20, 'foobar':30, 'bar': 40}
#    trie = marisa_trie.IntTrie().build(data)
#
#    for key, value in data.items():
#        assert trie[key] == value
#
#    trie['foo'] = 500
#    assert trie['foo'] == 500
#
#    # trie is frozen, no new keys are allowed
#    with pytest.raises(KeyError):
#        trie['z'] = 200
