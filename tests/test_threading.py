"""Tests for sharing the same object across threads.
Note that all other modules of this test suite run under pytest-run-parallel,
which tests that different objects can be created and consumed in parallel threads.
"""
from __future__ import annotations

import pickle
from functools import partial
from uuid import uuid4

import pytest
import hypothesis.strategies as st
from hypothesis import given, settings, HealthCheck

import marisa_trie

from .utils import text, records, run_threaded

pytestmark = [pytest.mark.thread_unsafe(reason="Test itself spawns threads")]


def parametrize(min_size: int = 0, max_size: int | None = None) -> pytest.MarkDecorator:
    return pytest.mark.parametrize(
        "cls,data_st",
        [
            pytest.param(
                marisa_trie.Trie,
                st.sets(text, min_size=min_size, max_size=max_size),
                id="Trie",
            ),
            pytest.param(
                marisa_trie.BinaryTrie,
                st.sets(st.binary(), min_size=min_size, max_size=max_size),
                id="BinaryTrie",
            ),
            pytest.param(
                marisa_trie.BytesTrie,
                st.dictionaries(
                    text, st.binary(), min_size=min_size, max_size=max_size
                ),
                id="BytesTrie",
            ),
            pytest.param(
                partial(marisa_trie.RecordTrie, "<H?"),
                st.dictionaries(text, records, min_size=min_size, max_size=max_size),
                id="RecordTrie",
            ),
        ],
    )


def make_trie(cls, data_st, data):
    contents = data.draw(data_st)
    if isinstance(contents, dict):
        trie = cls(contents.items())
        as_dict = {k: [v] for k, v in contents.items()}
    else:  # set of keys
        trie = cls(contents)
        as_dict = dict(trie)
        assert as_dict.keys() == contents
    return trie, as_dict


@parametrize(8, 8)  # Must be >= max_workers
@given(st.data())
def test_get_different_keys(cls, data_st, data):
    """Call __contains__, __getitem__, get, restore_key
    where multiple threads access different keys on the same container.
    """
    trie, as_dict = make_trie(cls, data_st, data)

    def f(i):
        key = list(as_dict)[i]
        value = as_dict[key]

        assert key in trie  # __contains__
        assert trie[key] == value  # __getitem__
        assert trie.get(key) == value
        if hasattr(trie, "restore_key"):
            assert trie.restore_key(value) == key

    run_threaded(f, pass_count=True, max_workers=8)


@parametrize(3, 3)
@given(st.data())
def test_get_same_key(cls, data_st, data):
    """Call __contains__, __getitem__, get, restore_key
    where multiple threads access the same key on the same container.
    """
    trie, as_dict = make_trie(cls, data_st, data)
    key = data.draw(st.sampled_from(list(as_dict)))
    value = as_dict[key]

    def f():
        assert key in trie  # __contains__
        assert trie[key] == value  # __getitem__
        assert trie.get(key) == value
        if hasattr(trie, "restore_key"):
            assert trie.restore_key(value) == key

    run_threaded(f)


@parametrize()
@given(st.data())
def test_iter(cls, data_st, data):
    """Different threads call __iter__, keys, iterkeys, items, iteritems
    on the same object
    """
    trie, as_dict = make_trie(cls, data_st, data)

    def f():
        keys = list(trie)  # __iter__
        assert list(trie.keys()) == keys
        assert list(trie.iterkeys()) == keys
        assert set(keys) == set(as_dict)

        items = list(trie.items())
        assert list(trie.iteritems()) == items
        assert [k for k, _ in items] == keys
        assert dict(items) == {
            k: v[0] if isinstance(v, list) else v for k, v in as_dict.items()
        }

    run_threaded(f)


@parametrize()
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data())
def test_saveload(tmp_path, cls, data_st, data):
    """Different threads call save() on the same object, to write different files."""
    trie, as_dict = make_trie(cls, data_st, data)

    def f():
        path = str(tmp_path / f"{uuid4()}.bin")
        trie.save(path)
        trie2 = cls().load(path)
        assert trie2 == trie
        assert dict(trie2) == as_dict

    run_threaded(f)


@parametrize()
@given(st.data())
def test_tobytes_frombytes(cls, data_st, data):
    """Different threads call tobytes() on the same object"""
    trie, as_dict = make_trie(cls, data_st, data)

    def f():
        bin = trie.tobytes()
        trie2 = cls().frombytes(bin)
        assert trie2 == trie
        assert dict(trie2) == as_dict

    run_threaded(f)


@parametrize()
@given(st.data())
def test_dumps_loads(cls, data_st, data):
    """Different threads call pickle.dumps() on the same object"""
    trie, as_dict = make_trie(cls, data_st, data)

    def f():
        pik = pickle.dumps(trie)
        trie2 = pickle.loads(pik)
        assert trie2 == trie
        assert dict(trie2) == as_dict

    run_threaded(f)
