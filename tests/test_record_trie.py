import io
import pickle

import hypothesis.strategies as st
from hypothesis import given

import marisa_trie

from .utils import text, records


@given(st.sets(st.tuples(text, records)))
def test_dumps_loads(data):
    trie = marisa_trie.RecordTrie("<H?", data)

    buf = io.BytesIO()
    pickle.dump(trie, buf)
    buf.seek(0)

    assert trie == pickle.load(buf)
