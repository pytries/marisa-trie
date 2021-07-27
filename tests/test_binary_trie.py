# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import pickle
from collections import Mapping

import pytest
import hypothesis.strategies as st
from hypothesis import given, assume

import marisa_trie


text = st.binary()


@given(st.sets(text), text)
def test_init(keys, missing_key):
    assume(missing_key not in keys)

    trie = marisa_trie.BinaryTrie(keys)
    for key in keys:
        assert key in trie

    assert missing_key not in trie


@given(st.sets(text, min_size=1), text)
def test_key_id(keys, missing_key):
    assume(missing_key not in keys)

    trie = marisa_trie.BinaryTrie(keys)
    for key in keys:
        key_id = trie.key_id(key)
        assert trie.restore_key(key_id) == key

    key_ids = [trie.key_id(key) for key in keys]
    non_existing_id = max(key_ids) + 1

    with pytest.raises(KeyError):
        trie.restore_key(non_existing_id)

    with pytest.raises(KeyError):
        trie.key_id(missing_key)


@given(st.sets(text, min_size=1), text)
def test_getitem(keys, missing_key):
    assume(missing_key not in keys)

    trie = marisa_trie.BinaryTrie(keys)
    for key in keys:
        key_id = trie[key]
        assert trie.restore_key(key_id) == key

    key_ids = [trie[key] for key in keys]
    non_existing_id = max(key_ids) + 1

    with pytest.raises(KeyError):
        trie.restore_key(non_existing_id)

    with pytest.raises(KeyError):
        trie[missing_key]


@given(st.sets(text))
def test_get(keys):
    trie = marisa_trie.BinaryTrie(keys)
    for key in keys:
        key_id = trie.get(key)
        assert trie.restore_key(key_id) == key

        key_id = trie.get(key, "default value")
        assert trie.restore_key(key_id) == key

    assert trie.get(b"non_existing_bytes_key") is None
    assert trie.get(b"non_existing_bytes_key", "default value") == "default value"


@given(st.sets(text))
def test_saveload(tmpdir, keys):
    trie = marisa_trie.BinaryTrie(keys)

    path = str(tmpdir.join("trie.bin"))
    with open(path, "wb") as f:
        trie.write(f)

    with open(path, "rb") as f:
        trie2 = marisa_trie.BinaryTrie()
        trie2.read(f)

    for key in keys:
        assert key in trie2


@given(st.sets(text))
def test_mmap(tmpdir, keys):
    trie = marisa_trie.BinaryTrie(keys)

    path = str(tmpdir.join("trie.bin"))
    with open(path, "wb") as f:
        trie.write(f)

    trie2 = marisa_trie.BinaryTrie()
    trie2.mmap(path)

    for key in keys:
        assert key in trie2


@given(st.sets(text))
def test_tobytes_frombytes(keys):
    trie = marisa_trie.BinaryTrie(keys)
    data = trie.tobytes()

    trie2 = marisa_trie.BinaryTrie().frombytes(data)

    for key in keys:
        assert key in trie2
        assert trie2.key_id(key) == trie.key_id(key)


@given(st.sets(text))
def test_dumps_loads(keys):
    trie = marisa_trie.BinaryTrie(keys)
    data = pickle.dumps(trie)

    trie2 = pickle.loads(data)

    for key in keys:
        assert key in trie2
        assert trie2.key_id(key) == trie.key_id(key)


def test_contains_empty():
    assert b"foo" not in marisa_trie.BinaryTrie()


def test_contains_singleton():
    trie = marisa_trie.BinaryTrie([b"foo"])
    assert b"foo" in trie
    assert b"f" not in trie


def test_eq_self():
    trie = marisa_trie.BinaryTrie()
    assert trie == trie
    assert trie == marisa_trie.BinaryTrie()


def test_eq_neq():
    trie = marisa_trie.BinaryTrie([b"foo", b"bar"])
    assert trie == marisa_trie.BinaryTrie([b"foo", b"bar"])
    assert trie != marisa_trie.BinaryTrie([b"foo", b"boo"])


def test_neq_different_type():
    assert marisa_trie.BinaryTrie([b"foo", b"bar"]) != {}


def test_eq_neq_different_order():
    lo_trie = marisa_trie.BinaryTrie(order=marisa_trie.LABEL_ORDER)
    wo_trie = marisa_trie.BinaryTrie(order=marisa_trie.WEIGHT_ORDER)
    assert lo_trie == lo_trie and wo_trie == wo_trie
    assert lo_trie != wo_trie


def test_gt_lt_exceptions():
    with pytest.raises(TypeError):
        marisa_trie.BinaryTrie() < marisa_trie.BinaryTrie()

    with pytest.raises(TypeError):
        marisa_trie.BinaryTrie() > marisa_trie.BinaryTrie()


def test_iter():
    trie = marisa_trie.BinaryTrie([b"foo", b"bar"])
    assert list(trie) == list(trie.iterkeys())


def test_len():
    trie = marisa_trie.BinaryTrie()
    assert len(trie) == 0

    trie = marisa_trie.BinaryTrie([b"foo", b"f", b"bar"])
    assert len(trie) == 3


def test_prefixes():
    trie = marisa_trie.BinaryTrie([b"foo", b"f", b"foobar", b"bar"])
    assert trie.prefixes(b"foobar") == [b"f", b"foo", b"foobar"]
    assert trie.prefixes(b"foo") == [b"f", b"foo"]
    assert trie.prefixes(b"bar") == [b"bar"]
    assert trie.prefixes(b"b") == []

    assert list(trie.iter_prefixes(b"foobar")) == [b"f", b"foo", b"foobar"]


def test_keys():
    keys = [b"foo", b"f", b"foobar", b"bar"]
    trie = marisa_trie.BinaryTrie(keys)
    assert set(trie.keys()) == set(keys)


def test_keys_prefix():
    keys = [b"foo", b"f", b"foobar", b"bar"]
    trie = marisa_trie.BinaryTrie(keys)
    assert set(trie.keys(b"fo")) == set([b"foo", b"foobar"])
    assert trie.keys(b"foobarz") == []


@given(st.sets(text))
def test_iterkeys(keys):
    trie = marisa_trie.BinaryTrie(keys)
    assert trie.keys() == list(trie.iterkeys())

    for key in keys:
        prefix = key[:5]
        assert trie.keys(prefix) == list(trie.iterkeys(prefix))


def test_items():
    keys = [b"foo", b"f", b"foobar", b"bar"]
    trie = marisa_trie.BinaryTrie(keys)
    items = trie.items()
    assert set(items) == set(zip(keys, (trie[k] for k in keys)))


def test_items_prefix():
    keys = [b"foo", b"f", b"foobar", b"bar"]
    trie = marisa_trie.BinaryTrie(keys)
    assert set(trie.items(b"fo")) == set(
        [
            (b"foo", trie[b"foo"]),
            (b"foobar", trie[b"foobar"]),
        ]
    )


@given(st.sets(text))
def test_iteritems(keys):
    trie = marisa_trie.BinaryTrie(keys)
    assert trie.items() == list(trie.iteritems())

    for key in keys:
        prefix = key[:5]
        assert trie.items(prefix) == list(trie.iteritems(prefix))


def test_has_keys_with_prefix_empty():
    empty_trie = marisa_trie.BinaryTrie()
    assert not empty_trie.has_keys_with_prefix(b"")
    assert not empty_trie.has_keys_with_prefix(b"ab")


def test_invalid_file():
    try:
        marisa_trie.BinaryTrie().load(__file__)
    except RuntimeError as e:
        assert "MARISA_FORMAT_ERROR" in e.args[0]
    else:
        pytest.fail("Exception is not raised")


def test_mutable_mapping():
    for method in Mapping.__abstractmethods__:
        assert hasattr(marisa_trie.BinaryTrie, method)
