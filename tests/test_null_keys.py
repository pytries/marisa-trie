import pickle

import pytest

import marisa_trie


KEYS = ["a", "a\0", "a\0b", "a\0bc", "ab", "é", "é\0€", "\0", "\0z"]


@pytest.fixture(params=["Trie", "StringTrie", "BytesTrie", "RecordTrie"])
def null_trie(request):
    kind = request.param
    if kind == "Trie":
        trie = marisa_trie.Trie(KEYS)
        values = {trie.restore_key(i): i for i in range(len(trie))}
    elif kind == "StringTrie":
        values = {key: "value\0" + str(i) for i, key in enumerate(KEYS)}
        trie = marisa_trie.StringTrie(values.items())
    elif kind == "BytesTrie":
        values = {key: b"value\0" + str(i).encode() for i, key in enumerate(KEYS)}
        trie = marisa_trie.BytesTrie(values.items())
    else:
        values = {key: (i,) for i, key in enumerate(KEYS)}
        trie = marisa_trie.RecordTrie("<I", values.items())
    return trie, values


def test_lookup(null_trie):
    trie, values = null_trie
    for key, value in values.items():
        expected = [value] if isinstance(trie, marisa_trie.BytesTrie) else value
        assert key in trie
        assert trie[key] == expected
        assert trie.get(key) == expected
        if isinstance(trie, (marisa_trie.Trie, marisa_trie.BytesTrie)):
            assert trie.get(key.encode("utf8")) == expected
        if isinstance(trie, marisa_trie.Trie):
            assert trie.key_id(key) == value
            assert trie.restore_key(value) == key


@pytest.mark.parametrize("key", ["a\0missing", "\0missing", "é\0missing"])
def test_missing_key(null_trie, key):
    trie, _ = null_trie
    assert key not in trie
    assert trie.get(key) is None
    assert trie.get(key, "default") == "default"
    with pytest.raises(KeyError):
        trie[key]


@pytest.mark.parametrize("prefix", ["", "a", "a\0", "é\0", "\0", "a\0missing"])
def test_predictive_search(null_trie, prefix):
    trie, values = null_trie
    expected = {key: value for key, value in values.items() if key.startswith(prefix)}
    assert sorted(trie.keys(prefix)) == sorted(expected)
    assert sorted(trie.iterkeys(prefix)) == sorted(expected)
    assert dict(trie.items(prefix)) == expected
    assert dict(trie.iteritems(prefix)) == expected


@pytest.mark.parametrize("query", ["a\0bcd", "é\0€x", "\0zx", "abx"])
def test_common_prefix_search(null_trie, query):
    trie, values = null_trie
    expected = {key: value for key, value in values.items() if query.startswith(key)}
    assert sorted(trie.prefixes(query)) == sorted(expected)
    if isinstance(trie, (marisa_trie.Trie, marisa_trie.StringTrie)):
        assert sorted(trie.iter_prefixes(query)) == sorted(expected)
    if isinstance(trie, marisa_trie.Trie):
        assert dict(trie.iter_prefixes_with_ids(query)) == expected


def test_pickle(null_trie):
    trie, values = null_trie
    loaded = pickle.loads(pickle.dumps(trie))
    for key, value in values.items():
        expected = [value] if isinstance(trie, marisa_trie.BytesTrie) else value
        assert loaded[key] == expected
    assert loaded.items("a\0") == trie.items("a\0")
