# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest
import io
import pickle

import marisa_trie
from .utils import get_random_words, get_random_binary


class TestBytesTrie(object):

    def data(self):
        keys = get_random_words(10000)
        values = [key.encode('cp1251') for key in keys]
        return list(zip(keys, values))

    def test_contains(self):
        data = self.data()
        trie = marisa_trie.BytesTrie(data)

        for key, value in data:
            assert key in trie

        non_key = '2135'
        assert non_key not in trie


    def test_getitem_fuzzy(self):
        data = self.data()
        trie = marisa_trie.BytesTrie(data)

        for key, value in data:
            assert trie[key] == [value]

        with pytest.raises(KeyError):
            trie['2135']

    def test_getitem_multiple(self):
        data = [
            ('foo', b'x'),
            ('fo',  b'y'),
            ('foo', b'a'),
        ]
        trie = marisa_trie.BytesTrie(data)
        assert trie['fo'] == [b'y']
        assert trie['foo'] == [b'a', b'x']

    def test_null_bytes_in_values(self):
        keys = get_random_words(10000)
        values = get_random_binary(10000)

        assert any(b'\x00' in p for p in values)

        data = zip(keys, values)
        trie = marisa_trie.BytesTrie(data)

        for key, value in data:
            assert trie[key] == [value]


    def test_keys(self):
        trie = marisa_trie.BytesTrie([
            ('foo', b'x'),
            ('fo',  b'y'),
            ('foo', b'a'),
        ])

        # FIXME: ordering?
        assert trie.keys() == ['foo', 'foo', 'fo']
        assert trie.keys('f') == ['foo', 'foo', 'fo']
        assert trie.keys('fo') == ['foo', 'foo', 'fo']
        assert trie.keys('foo') == ['foo', 'foo']
        assert trie.keys('food') == []
        assert trie.keys('bar') == []

    def test_items(self):
        data = [
            ('fo',  b'y'),
            ('foo', b'x'),
            ('foo', b'a'),
        ]
        trie = marisa_trie.BytesTrie(data)
        assert set(trie.items()) == set(data)
        assert set(trie.items('f')) == set(data)
        assert set(trie.items('fo')) == set(data)
        assert set(trie.items('foo')) == set(data[1:])
        assert trie.items('food') == []
        assert trie.items('bar') == []

    def test_pickling(self):
        trie = marisa_trie.BytesTrie([
            ('foo', b'foo'),
            ('bar', b'bar'),
        ])
        buf = io.BytesIO()
        pickle.dump(trie, buf)
        buf.seek(0)

        trie2 = pickle.load(buf)
        assert trie2['foo'] == [b'foo']
        assert trie2['bar'] == [b'bar']



class TestRecordTrie(object):

    def data(self):
        keys = get_random_words(10000)
        values = [(len(key), 'ё' in key) for key in keys]
        fmt = str("<H?")
        return fmt, list(zip(keys, values))


    def test_getitem(self):
        fmt, data = self.data()
        trie = marisa_trie.RecordTrie(fmt, data)

        for key, value in data:
            assert trie[key] == [value]

        with pytest.raises(KeyError):
            trie['2135']

    def test_items(self):
        fmt, data = self.data()
        trie = marisa_trie.RecordTrie(fmt, data)

        assert set(trie.items()) == set(data)

    def test_prefixes(self):
        trie = marisa_trie.RecordTrie(str("<H"), [
            ('foo', [1]),
            ('bar',  [2]),
            ('foobar', [3]),
        ])
        assert trie.prefixes('foo') == ['foo']
        assert trie.prefixes('foobar') == ['foo', 'foobar']
        assert trie.prefixes('bara') == ['bar']
        assert trie.prefixes('f') == []

    def test_get(self):
        trie = marisa_trie.RecordTrie(str("<H"), [
            ('foo', [1]),
            ('bar',  [2]),
            ('foobar', [3]),
        ])

        assert trie.get('foo') == [(1,)]
        assert trie.get('foo', [(55,)]) == [(1,)]
        assert trie.get('FOO') is None
        assert trie.get('FOO', [(55,)]) == [(55,)]
        assert trie.get('FOO', 123) == 123

    def test_pickling(self):
        trie = marisa_trie.RecordTrie(str("<H"), [
            ('foo', [1]),
            ('bar', [2]),
        ])
        buf = io.BytesIO()
        pickle.dump(trie, buf)
        buf.seek(0)

        trie2 = pickle.load(buf)
        assert trie2['foo'] == [(1,)]
        assert trie2['bar'] == [(2,)]

