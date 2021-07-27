# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import pickle
from collections import Mapping

import pytest
import hypothesis.strategies as st
from hypothesis import given, assume

import marisa_trie
from .utils import text


@given(st.sets(text), text)
def test_init(keys, missing_key):
    assume(missing_key not in keys)

    trie = marisa_trie.Trie(keys)
    for key in keys:
        assert key in trie

    assert missing_key not in trie


@given(st.sets(text, min_size=1), text)
def test_key_id(keys, missing_key):
    assume(missing_key not in keys)

    trie = marisa_trie.Trie(keys)
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

    trie = marisa_trie.Trie(keys)
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
    trie = marisa_trie.Trie(keys)
    for key in keys:
        key_id = trie.get(key)
        assert trie.restore_key(key_id) == key

        key_id = trie.get(key.encode("utf8"))
        assert trie.restore_key(key_id) == key

        key_id = trie.get(key, "default value")
        assert trie.restore_key(key_id) == key

    assert trie.get("non_existing_key") is None
    assert trie.get(b"non_existing_bytes_key") is None
    assert trie.get("non_existing_key", "default value") == "default value"
    assert trie.get(b"non_existing_bytes_key", "default value") == "default value"


@given(st.sets(text))
def test_saveload(tmpdir, keys):
    trie = marisa_trie.Trie(keys)

    path = str(tmpdir.join("trie.bin"))
    with open(path, "wb") as f:
        trie.write(f)

    with open(path, "rb") as f:
        trie2 = marisa_trie.Trie()
        trie2.read(f)

    for key in keys:
        assert key in trie2


@given(st.sets(text))
def test_mmap(tmpdir, keys):
    trie = marisa_trie.Trie(keys)

    path = str(tmpdir.join("trie.bin"))
    with open(path, "wb") as f:
        trie.write(f)

    trie2 = marisa_trie.Trie()
    trie2.mmap(path)

    for key in keys:
        assert key in trie2


@given(st.sets(text))
def test_tobytes_frombytes(keys):
    trie = marisa_trie.Trie(keys)
    data = trie.tobytes()

    trie2 = marisa_trie.Trie().frombytes(data)

    for key in keys:
        assert key in trie2
        assert trie2.key_id(key) == trie.key_id(key)


@given(st.sets(text))
def test_dumps_loads(keys):
    trie = marisa_trie.Trie(keys)
    data = pickle.dumps(trie)

    trie2 = pickle.loads(data)

    for key in keys:
        assert key in trie2
        assert trie2.key_id(key) == trie.key_id(key)


def test_contains_empty():
    assert "foo" not in marisa_trie.Trie()


def test_contains_singleton():
    trie = marisa_trie.Trie(["foo"])
    assert "foo" in trie
    assert "f" not in trie


def test_eq_self():
    trie = marisa_trie.Trie()
    assert trie == trie
    assert trie == marisa_trie.Trie()


def test_eq_neq():
    trie = marisa_trie.Trie(["foo", "bar"])
    assert trie == marisa_trie.Trie(["foo", "bar"])
    assert trie != marisa_trie.Trie(["foo", "boo"])


def test_neq_different_type():
    assert marisa_trie.Trie(["foo", "bar"]) != {}


def test_eq_neq_different_order():
    lo_trie = marisa_trie.Trie(order=marisa_trie.LABEL_ORDER)
    wo_trie = marisa_trie.Trie(order=marisa_trie.WEIGHT_ORDER)
    assert lo_trie == lo_trie and wo_trie == wo_trie
    assert lo_trie != wo_trie


def test_gt_lt_exceptions():
    with pytest.raises(TypeError):
        marisa_trie.Trie() < marisa_trie.Trie()

    with pytest.raises(TypeError):
        marisa_trie.Trie() > marisa_trie.Trie()


def test_iter():
    trie = marisa_trie.Trie(["foo", "bar"])
    assert list(trie) == list(trie.iterkeys())


def test_len():
    trie = marisa_trie.Trie()
    assert len(trie) == 0

    trie = marisa_trie.Trie(["foo", "f", "bar"])
    assert len(trie) == 3


def test_prefixes():
    trie = marisa_trie.Trie(["foo", "f", "foobar", "bar"])
    assert trie.prefixes("foobar") == ["f", "foo", "foobar"]
    assert trie.prefixes("foo") == ["f", "foo"]
    assert trie.prefixes("bar") == ["bar"]
    assert trie.prefixes("b") == []

    assert list(trie.iter_prefixes("foobar")) == ["f", "foo", "foobar"]


def test_keys():
    keys = ["foo", "f", "foobar", "bar"]
    trie = marisa_trie.Trie(keys)
    assert set(trie.keys()) == set(keys)


def test_keys_prefix():
    keys = ["foo", "f", "foobar", "bar"]
    trie = marisa_trie.Trie(keys)
    assert set(trie.keys("fo")) == set(["foo", "foobar"])
    assert trie.keys("foobarz") == []


@given(st.sets(text))
def test_iterkeys(keys):
    trie = marisa_trie.Trie(keys)
    assert trie.keys() == list(trie.iterkeys())

    for key in keys:
        prefix = key[:5]
        assert trie.keys(prefix) == list(trie.iterkeys(prefix))


def test_items():
    keys = ["foo", "f", "foobar", "bar"]
    trie = marisa_trie.Trie(keys)
    items = trie.items()
    assert set(items) == set(zip(keys, (trie[k] for k in keys)))


def test_items_prefix():
    keys = ["foo", "f", "foobar", "bar"]
    trie = marisa_trie.Trie(keys)
    assert set(trie.items("fo")) == set(
        [
            ("foo", trie["foo"]),
            ("foobar", trie["foobar"]),
        ]
    )


@given(st.sets(text))
def test_iteritems(keys):
    trie = marisa_trie.Trie(keys)
    assert trie.items() == list(trie.iteritems())

    for key in keys:
        prefix = key[:5]
        assert trie.items(prefix) == list(trie.iteritems(prefix))


def test_has_keys_with_prefix_empty():
    empty_trie = marisa_trie.Trie()
    assert not empty_trie.has_keys_with_prefix("")
    assert not empty_trie.has_keys_with_prefix("ab")


def test_has_keys_with_prefix():
    fruit_trie = marisa_trie.BytesTrie(
        [
            ("apple", b"foo"),
            ("pear", b"bar"),
            ("peach", b"baz"),
        ]
    )
    assert fruit_trie.has_keys_with_prefix("")
    assert fruit_trie.has_keys_with_prefix("a")
    assert fruit_trie.has_keys_with_prefix("pe")
    assert fruit_trie.has_keys_with_prefix("pear")
    assert not fruit_trie.has_keys_with_prefix("x")


def test_invalid_file():
    try:
        marisa_trie.Trie().load(__file__)
    except RuntimeError as e:
        assert "MARISA_FORMAT_ERROR" in e.args[0]
    else:
        pytest.fail("Exception is not raised")


def test_mutable_mapping():
    for method in Mapping.__abstractmethods__:
        assert hasattr(marisa_trie.Trie, method)
