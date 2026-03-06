import io
import pickle
from collections.abc import Mapping
from uuid import uuid4

import pytest
import hypothesis.strategies as st
from hypothesis import assume, given, settings, HealthCheck

import marisa_trie

from .utils import text


@given(st.dictionaries(text, text), text)
def test_init(data, missing_key):
    assume(missing_key not in data)

    trie = marisa_trie.StringTrie(data.items())
    for key in data:
        assert key in trie
        assert trie[key] == data[key]

    assert missing_key not in trie


@given(st.dictionaries(text, text))
def test_get(data):
    trie = marisa_trie.StringTrie(data.items())

    for key, value in data.items():
        assert trie.get(key) == value

    assert trie.get("non_existing_key") is None
    assert trie.get("non_existing_key", "default value") == "default value"


@pytest.mark.parametrize("data", [[], [("foo", "bar")]])
def test_getitem_missing(data):
    trie = marisa_trie.StringTrie(data)
    with pytest.raises(KeyError):
        trie["missing"]


def test_duplicate_keys_disallowed():
    with pytest.raises(ValueError):
        marisa_trie.StringTrie([("foo", "x"), ("foo", "y")])


def test_duplicate_values_allowed():
    trie = marisa_trie.StringTrie([("foo", "x"), ("bar", "x")])
    assert trie["foo"] == "x"
    assert trie["bar"] == "x"


def test_prefixes():
    trie = marisa_trie.StringTrie(
        [("foo", "x"), ("f", "y"), ("foobar", "z"), ("bar", "w")]
    )
    assert trie.prefixes("foobar") == ["f", "foo", "foobar"]
    assert trie.prefixes("foo") == ["f", "foo"]
    assert trie.prefixes("bar") == ["bar"]
    assert trie.prefixes("b") == []

    assert list(trie.iter_prefixes("foobar")) == ["f", "foo", "foobar"]


def test_prefix_items():
    trie = marisa_trie.StringTrie(
        [("foo", "x"), ("f", "y"), ("foobar", "z"), ("bar", "w")]
    )
    assert trie.prefix_items("foobar") == [("f", "y"), ("foo", "x"), ("foobar", "z")]
    assert list(trie.iter_prefix_items("foo")) == [("f", "y"), ("foo", "x")]
    assert trie.prefix_items("b") == []


@given(st.dictionaries(text, text))
def test_iter(data):
    trie = marisa_trie.StringTrie(data.items())
    assert trie.keys() == list(trie.iterkeys())
    assert trie.values() == list(trie.itervalues())
    assert trie.items() == list(trie.iteritems())

    for key in data:
        prefix = key[:5]
        assert trie.keys(prefix) == list(trie.iterkeys(prefix))
        assert trie.values(prefix) == list(trie.itervalues(prefix))
        assert trie.items(prefix) == list(trie.iteritems(prefix))


@given(st.dictionaries(text, text))
def test_items_roundtrip(data):
    trie = marisa_trie.StringTrie(data.items())
    assert dict(trie.items()) == data


def test_accessors():
    trie = marisa_trie.StringTrie([("foo", "x"), ("bar", "y")])
    assert isinstance(trie.key_trie, marisa_trie.Trie)
    assert isinstance(trie.value_trie, marisa_trie.Trie)
    assert "foo" in trie.key_trie
    assert "x" in trie.value_trie


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.dictionaries(text, text))
def test_saveload(tmp_path, data):
    trie = marisa_trie.StringTrie(data.items())

    path = str(tmp_path / f"{uuid4()}.bin")
    trie.save(path)

    trie2 = marisa_trie.StringTrie().load(path)
    assert trie2 == trie
    assert dict(trie2.items()) == data


@given(st.dictionaries(text, text))
def test_tobytes_frombytes(data):
    trie = marisa_trie.StringTrie(data.items())
    blob = trie.tobytes()

    trie2 = marisa_trie.StringTrie().frombytes(blob)
    assert trie2 == trie
    assert dict(trie2.items()) == data


@given(st.dictionaries(text, text))
def test_dumps_loads(data):
    trie = marisa_trie.StringTrie(data.items())

    buf = io.BytesIO()
    pickle.dump(trie, buf)
    buf.seek(0)

    trie2 = pickle.load(buf)
    assert trie2 == trie
    assert dict(trie2.items()) == data


def test_mapping():
    for method in Mapping.__abstractmethods__:
        assert hasattr(marisa_trie.StringTrie, method)


def test_frombytes_invalid_magic():
    trie = marisa_trie.StringTrie()
    with pytest.raises(ValueError):
        trie.frombytes(b"not-a-valid-stringtrie")
