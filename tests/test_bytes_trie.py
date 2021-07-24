# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import io
import pickle

import pytest
import hypothesis.strategies as st
from hypothesis import assume, given

import marisa_trie
from .utils import text


@given(st.sets(text), st.lists(st.binary()), text)
def test_contains(keys, values, missing_key):
    assume(missing_key not in keys)

    data = zip(keys, values)
    trie = marisa_trie.BytesTrie(data)

    for word, value in data:
        assert word in trie

    assert missing_key not in trie


@given(st.sets(text), st.lists(st.binary()), text)
def test_getitem(keys, values, missing_key):
    assume(missing_key not in keys)

    data = zip(keys, values)
    trie = marisa_trie.BytesTrie(data)

    for key, value in data:
        assert trie[key] == [value]

    with pytest.raises(KeyError):
        trie[missing_key]


@pytest.mark.parametrize("data", [[], [("foo", b"bar")]])
def test_getitem_missing(data):
    trie = marisa_trie.BytesTrie(data)
    with pytest.raises(KeyError):
        trie["missing"]


def test_getitem_multiple():
    data = [
        ("foo", b"x"),
        ("fo", b"y"),
        ("foo", b"a"),
    ]
    trie = marisa_trie.BytesTrie(data)
    assert trie["fo"] == [b"y"]
    assert trie["foo"] == [b"a", b"x"]


def test_null_bytes_in_values():
    data = [("foo", b"\x00\x00bar\x00")]
    trie = marisa_trie.BytesTrie(data)

    for key, value in data:
        assert trie[key] == [value]


def test_items():
    data = [
        ("fo", b"y"),
        ("foo", b"x"),
        ("foo", b"a"),
    ]
    trie = marisa_trie.BytesTrie(data)
    assert set(trie.items()) == set(data)
    assert set(trie.items("f")) == set(data)
    assert set(trie.items("fo")) == set(data)
    assert set(trie.items("foo")) == set(data[1:])
    assert trie.items("food") == []
    assert trie.items("bar") == []


@given(st.sets(text), st.lists(st.binary()))
def test_iteritems(keys, values):
    trie = marisa_trie.BytesTrie(zip(keys, values))
    assert trie.items() == list(trie.iteritems())

    for key in keys:
        prefix = key[:5]
        assert trie.items(prefix) == list(trie.iteritems(prefix))


def test_keys():
    trie = marisa_trie.BytesTrie(
        [
            ("foo", b"x"),
            ("fo", b"y"),
            ("foo", b"a"),
        ]
    )

    # FIXME: ordering?
    assert trie.keys() == ["foo", "foo", "fo"]
    assert trie.keys("f") == ["foo", "foo", "fo"]
    assert trie.keys("fo") == ["foo", "foo", "fo"]
    assert trie.keys("foo") == ["foo", "foo"]
    assert trie.keys("food") == []
    assert trie.keys("bar") == []


@given(st.sets(text), st.lists(st.binary()))
def test_iterkeys(keys, values):
    trie = marisa_trie.BytesTrie(zip(keys, values))
    assert trie.keys() == list(trie.iterkeys())

    for key in keys:
        prefix = key[:5]
        assert trie.keys(prefix) == list(trie.iterkeys(prefix))


@given(st.sets(st.tuples(text, st.binary())))
def test_dumps_loads(data):
    trie = marisa_trie.BytesTrie(data)

    buf = io.BytesIO()
    pickle.dump(trie, buf)
    buf.seek(0)

    assert trie == pickle.load(buf)
