# cython: profile=False
from __future__ import unicode_literals

from std_iostream cimport stringstream, istream, ostream
from libc.string cimport strncmp
cimport keyset
cimport key
cimport query
cimport agent
cimport trie
cimport iostream
cimport base

import itertools
import struct

try:
    from itertools import izip
except ImportError:
    izip = zip


DEFAULT_CACHE = base.MARISA_DEFAULT_CACHE
HUGE_CACHE = base.MARISA_HUGE_CACHE
LARGE_CACHE = base.MARISA_LARGE_CACHE
NORMAL_CACHE = base.MARISA_NORMAL_CACHE
SMALL_CACHE = base.MARISA_SMALL_CACHE
TINY_CACHE = base.MARISA_TINY_CACHE

MIN_NUM_TRIES = base.MARISA_MIN_NUM_TRIES
MAX_NUM_TRIES = base.MARISA_MAX_NUM_TRIES
DEFAULT_NUM_TRIES = base.MARISA_DEFAULT_NUM_TRIES

# MARISA_TEXT_TAIL merges last labels as zero-terminated strings. So, it is
# available if and only if the last labels do not contain a NULL character.
# If MARISA_TEXT_TAIL is specified and a NULL character exists in the last
# labels, the setting is automatically switched to MARISA_BINARY_TAIL.
TEXT_TAIL = base.MARISA_TEXT_TAIL

# MARISA_BINARY_TAIL also merges last labels but as byte sequences. It uses
# a bit vector to detect the end of a sequence, instead of NULL characters.
# So, MARISA_BINARY_TAIL requires a larger space if the average length of
# labels is greater than 8.
BINARY_TAIL = base.MARISA_BINARY_TAIL
DEFAULT_TAIL = base.MARISA_DEFAULT_TAIL


# MARISA_LABEL_ORDER arranges nodes in ascending label order.
# MARISA_LABEL_ORDER is useful if an application needs to predict keys in
# label order.
LABEL_ORDER = base.MARISA_LABEL_ORDER

# MARISA_WEIGHT_ORDER arranges nodes in descending weight order.
# MARISA_WEIGHT_ORDER is generally a better choice because it enables faster
# matching.
WEIGHT_ORDER = base.MARISA_WEIGHT_ORDER
DEFAULT_ORDER = base.MARISA_DEFAULT_ORDER

cdef unicode _get_key(agent.Agent& ag):
    return <unicode>(ag.key().ptr()[:ag.key().length()].decode('utf8'))


cdef class _Trie:
    """
    Base MARISA-trie wrapper.
    It can store unicode keys and assign an unque ID to each key.
    """

    cdef trie.Trie* _trie

    def __init__(self, arg=None, num_tries=DEFAULT_NUM_TRIES, binary=False,
                       cache_size=DEFAULT_CACHE, order=DEFAULT_ORDER,
                       weights=None):
        """
        ``arg`` can be one of the following:

        * an iterable with unicode keys;
        * None (if you're going to load a trie later).

        Pass a ``weights`` iterable with expected lookup frequences
        to optimize lookup and prefix search speed.
        """

        if self._trie:
            return
        self._trie = new trie.Trie()

        byte_keys = (key.encode('utf8') for key in (arg or []))

        self._build(
            byte_keys,
            weights,
            num_tries=num_tries,
            binary=binary,
            cache_size=cache_size,
            order=order
        )

    def __dealloc__(self):
        if self._trie:
            del self._trie

    def _config_flags(self, num_tries=DEFAULT_NUM_TRIES, binary=False,
                            cache_size=DEFAULT_CACHE, order=DEFAULT_ORDER):

        if not MIN_NUM_TRIES <= num_tries <= MAX_NUM_TRIES:
            raise ValueError("num_tries (which is %d) must be between between %d and %d" % (num_tries, MIN_NUM_TRIES, MAX_NUM_TRIES))

        binary_flag = BINARY_TAIL if binary else TEXT_TAIL
        return num_tries | binary_flag | cache_size | order

    def _build(self, byte_keys, weights=None, **options):
        """
        Build the trie using values from ``byte_keys`` iterable.
        """
        if weights is None:
            weights = itertools.repeat(1.0)

        cdef char* data
        cdef float weight
        cdef keyset.Keyset *ks = new keyset.Keyset()

        try:
            for key, weight in izip(byte_keys, weights):
                data = key # cast to char*
                ks.push_back(data, len(key), weight)
            self._trie.build(ks[0], self._config_flags(**options))
        finally:
            del ks

    def __richcmp__(self, other, int op):
        if op == 2:    # ==
            if other is self:
                return True
            elif not isinstance(other, _Trie):
                return False

            return (<_Trie>self)._equals(other)
        elif op == 3:  # !=
            return not (self == other)

        raise TypeError("unorderable types: {0} and {1}".format(
            self.__class__, other.__class__))

    cdef bint _equals(self, _Trie other) nogil:
        cdef int num_keys = self._trie.num_keys()
        cdef base.NodeOrder node_order = self._trie.node_order()
        if (other._trie.num_keys() != num_keys or
            other._trie.node_order() != node_order):
            return False

        cdef agent.Agent ag1, ag2
        ag1.set_query(b"")
        ag2.set_query(b"")
        cdef int i
        cdef key.Key key1, key2
        for i in range(num_keys):
            self._trie.predictive_search(ag1)
            other._trie.predictive_search(ag2)
            key1 = ag1.key()
            key2 = ag2.key()
            if (key1.length() != key2.length() or
                strncmp(key1.ptr(), key2.ptr(), key1.length()) != 0):
                return False
        return True

    def __iter__(self):
        return self.iterkeys()

    def __len__(self):
        return self._trie.num_keys()

    def __contains__(self, unicode key):
        cdef bytes _key = <bytes>key.encode('utf8')
        return self._contains(_key)

    cdef bint _contains(self, bytes key):
        cdef agent.Agent ag
        ag.set_query(key)
        return self._trie.lookup(ag)

    def read(self, f):
        """
        Read a trie from an open file object.

        Works only with "real" disk-based file objects,
        file-like objects are not supported.
        """
        self._trie.read(f.fileno())
        return self

    def write(self, f):
        """
        Read a trie to an open file object.

        Works only with "real" disk-based file objects,
        file-like objects are not supported.
        """
        self._trie.write(f.fileno())

    def save(self, path):
        """ Save trie to a file. """
        with open(path, 'w') as f:
            self.write(f)

    def load(self, path):
        """ Load trie from a file. """
        with open(path, 'r') as f:
            self.read(f)
        return self

    cpdef bytes tobytes(self) except +:
        """
        Return raw trie content as bytes.
        """
        cdef stringstream stream
        iostream.write((<ostream *> &stream)[0], self._trie[0])
        cdef bytes res = stream.str()
        return res

    cpdef frombytes(self, bytes data) except +:
        """
        Load a trie from bytes ``data``.
        """
        cdef stringstream* stream = new stringstream(data)
        try:
            iostream.read((<istream *> stream)[0], self._trie)
        finally:
            del stream
        return self

    def __reduce__(self): # pickling support
        return self.__class__, tuple(), self.tobytes()

    def __setstate__(self, state): # pickling support
        self.frombytes(state)

    def mmap(self, path):
        """
        Mmap trie to a file; this allows lookups without loading full
        trie to memory.
        """
        import sys
        str_path = path.encode(sys.getfilesystemencoding())
        cdef char* c_path = str_path
        self._trie.mmap(c_path)
        return self

    def iterkeys(self, unicode prefix=""):
        """
        Return an iterator over keys that have a prefix ``prefix``.
        """
        cdef agent.Agent ag
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            yield _get_key(ag)

    cpdef list keys(self, unicode prefix=""):
        """
        Return a list with all keys with a prefix ``prefix``.
        """
        # non-generator inlined version of iterkeys()
        cdef list res = []
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        cdef agent.Agent ag
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            res.append(_get_key(ag))

        return res

    def has_keys_with_prefix(self, unicode prefix=""):
        """
        Returns True if any key in the trie begins with ``prefix``.
        """
        cdef agent.Agent ag
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        ag.set_query(b_prefix)
        return self._trie.predictive_search(ag)


cdef class Trie(_Trie):
    """
    This trie stores unicode keys and assigns an unque ID to each key.
    """

    # key_id method is not in _Trie because it won't work for BytesTrie
    cpdef int key_id(self, unicode key) except -1:
        """
        Return unique auto-generated key index for a ``key``.
        Raises KeyError if key is not in this trie.
        """
        cdef bytes _key = <bytes>key.encode('utf8')
        cdef int res = self._key_id(_key)
        if res == -1:
            raise KeyError(key)
        return res

    def __getitem__(self, unicode key):
        return self.key_id(key)

    def get(self, key, default=None):
        """
        Return a key id for a given key or ``default`` if the key is not found.
        """
        cdef bytes b_key
        cdef int res

        if isinstance(key, unicode):
            b_key = <bytes>(<unicode>key).encode('utf8')
        else:
            b_key = key

        res = self._key_id(b_key)
        if res == -1:
            return default
        return res

    cpdef restore_key(self, int index):
        """
        Return a key given its index (obtained by ``key_id`` method).
        """
        cdef agent.Agent ag
        ag.set_query(index)
        try:
            self._trie.reverse_lookup(ag)
        except KeyError:
            raise KeyError(index)
        return _get_key(ag)

    cdef int _key_id(self, char* key):
        cdef bint res
        cdef agent.Agent ag
        ag.set_query(key)
        res = self._trie.lookup(ag)
        if not res:
            return -1
        return ag.key().id()

    def iter_prefixes(self, unicode key):
        """
        Return an iterator of all prefixes of a given key.
        """
        cdef bytes b_key = <bytes>key.encode('utf8')
        cdef agent.Agent ag
        ag.set_query(b_key)

        while self._trie.common_prefix_search(ag):
            yield _get_key(ag)

    def prefixes(self, unicode key):
        """
        Return a list with all prefixes of a given key.
        """
        # this an inlined version of ``list(self.iter_prefixes(key))``

        cdef list res = []
        cdef bytes b_key = <bytes>key.encode('utf8')
        cdef agent.Agent ag
        ag.set_query(b_key)

        while self._trie.common_prefix_search(ag):
            res.append(_get_key(ag))
        return res

    def iteritems(self, unicode prefix=""):
        """
        Return an iterator over items that have a prefix ``prefix``.
        """
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        cdef agent.Agent ag
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            yield _get_key(ag), ag.key().id()

    def items(self, unicode prefix=""):
        # inlined for speed
        cdef list res = []
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        cdef agent.Agent ag
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            res.append((_get_key(ag), ag.key().id()))

        return res


# This symbol is not allowed in utf8 so it is safe to use
# as a separator between utf8-encoded string and binary payload.
# XXX: b'\xff' value changes sort order for BytesTrie and RecordTrie.
# See https://github.com/kmike/DAWG docs for a description of a similar issue.
cdef bytes _VALUE_SEPARATOR = b'\xff'


cdef class BytesTrie(_Trie):
    """
    This class implements read-only Trie-based
    {unicode -> list of bytes objects} mapping.

    This mapping is implemented by appending binary values to
    utf8-encoded keys and storing the result in MARISA-trie.
    """

    cdef bytes _b_value_separator
    cdef unsigned char _c_value_separator

    def __init__(self, arg=None, bytes value_separator=_VALUE_SEPARATOR, **options):
        """
        ``arg`` must be an iterable of tuples (unicode_key, bytes_payload).
        """
        super(BytesTrie, self).__init__()

        self._b_value_separator = value_separator
        self._c_value_separator = <unsigned char>ord(value_separator)

        byte_keys = (self._raw_key(d[0], d[1]) for d in (arg or []))
        self._build(byte_keys, **options)

    cpdef bytes _raw_key(self, unicode key, bytes payload):
        return key.encode('utf8') + self._b_value_separator + payload

    cdef bint _contains(self, bytes key):
        cdef agent.Agent ag
        cdef bytes _key = key + self._b_value_separator
        ag.set_query(_key)
        return self._trie.predictive_search(ag)

    cpdef list prefixes(self, unicode key):
        """
        Return a list with all prefixes of a given key.
        """

        # XXX: is there a char-walking API in libmarisa?
        # This implementation is suboptimal.

        cdef agent.Agent ag
        cdef list res = []
        cdef int key_len = len(key)
        cdef unicode prefix
        cdef bytes b_prefix
        cdef int ind = 1

        while ind <= key_len:
            prefix = key[:ind]
            b_prefix = <bytes>(prefix.encode('utf8') + self._b_value_separator)
            ag.set_query(b_prefix)
            if self._trie.predictive_search(ag):
                res.append(prefix)

            ind += 1

        return res

    def __getitem__(self, key):
        cdef list res = self.get(key)
        if res is None:
            raise KeyError(key)
        return res

    cpdef get(self, key, default=None):
        """
        Return a list of payloads (as byte objects) for a given key
        or ``default`` if the key is not found.
        """
        cdef list res

        if isinstance(key, unicode):
            res = self.get_value(<unicode>key)
        else:
            res = self.b_get_value(key)

        if not res:
            return default
        return res

    cpdef list get_value(self, unicode key):
        """
        Return a list of payloads (as byte objects) for a given unicode key.
        """
        cdef bytes b_key = <bytes>key.encode('utf8')
        return self.b_get_value(b_key)

    cpdef list b_get_value(self, bytes key):
        """
        Return a list of payloads (as byte objects) for a given utf8-encoded key.
        """
        cdef list res = []
        cdef bytes value
        cdef bytes b_prefix = key + self._b_value_separator
        cdef int prefix_len = len(b_prefix)

        cdef agent.Agent ag
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            value = ag.key().ptr()[prefix_len:ag.key().length()]
            res.append(value)

        return res

    cpdef list items(self, unicode prefix=""):
        # copied from iteritems for speed
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        cdef bytes value
        cdef unicode key
        cdef unsigned char* raw_key
        cdef list res = []
        cdef int i, value_len

        cdef agent.Agent ag
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            raw_key = <unsigned char*>ag.key().ptr()

            for i in range(0, ag.key().length()):
                if raw_key[i] == self._c_value_separator:
                    break

            key = raw_key[:i].decode('utf8')
            value = raw_key[i+1:ag.key().length()]

            res.append(
                (key, value)
            )
        return res

    def iteritems(self, unicode prefix=""):
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        cdef bytes value
        cdef unicode key
        cdef unsigned char* raw_key
        cdef int i, value_len

        cdef agent.Agent ag
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            raw_key = <unsigned char*>ag.key().ptr()

            for i in range(0, ag.key().length()):
                if raw_key[i] == self._c_value_separator:
                    break

            key = raw_key[:i].decode('utf8')
            value = raw_key[i+1:ag.key().length()]

            yield key, value

    cpdef list keys(self, unicode prefix=""):
        # copied from iterkeys for speed
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        cdef unicode key
        cdef unsigned char* raw_key
        cdef list res = []
        cdef int i

        cdef agent.Agent ag
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            raw_key = <unsigned char*>ag.key().ptr()

            for i in range(0, ag.key().length()):
                if raw_key[i] == self._c_value_separator:
                    key = raw_key[:i].decode('utf8')
                    res.append(key)
                    break
        return res

    def iterkeys(self, unicode prefix=""):
        cdef bytes b_prefix = <bytes>prefix.encode('utf8')
        cdef unicode key
        cdef unsigned char* raw_key
        cdef int i

        cdef agent.Agent ag
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            raw_key = <unsigned char*>ag.key().ptr()

            for i in range(0, ag.key().length()):
                if raw_key[i] == self._c_value_separator:
                    yield raw_key[:i].decode('utf8')
                    break


cdef class _UnpackTrie(BytesTrie):

    def __init__(self, arg=None, **options):
        keys = ((d[0], self._pack(d[1])) for d in (arg or []))
        super(_UnpackTrie, self).__init__(keys, **options)

    cdef _unpack(self, bytes value):
        return value

    cdef bytes _pack(self, value):
        return value

    cpdef list b_get_value(self, bytes key):
        cdef list values = BytesTrie.b_get_value(self, key)
        return [self._unpack(val) for val in values]

    cpdef list items(self, unicode prefix=""):
        cdef list items = BytesTrie.items(self, prefix)
        return [(key, self._unpack(val)) for (key, val) in items]

    def iteritems(self, unicode prefix=""):
        return ((key, self._unpack(val)) for key, val in BytesTrie.iteritems(self, prefix))


cdef class RecordTrie(_UnpackTrie):
    """
    This class implements read-only Trie-based
    {unicode -> list of tuples} mapping where all tuples are of the
    same structure and may be packed with the same format string
    using python ``struct`` module from the standard library.

    The payload format must be defined at creation time using ``fmt``
    constructor argument; it has the same meaning as ``fmt`` argument
    for functions from ``struct`` module; take a look at
    http://docs.python.org/library/struct.html#format-strings for the
    specification.

    This mapping is implemented by appending binary values to
    utf8-encoded keys and storing the result in MARISA-trie.
    """
    cdef _struct
    cdef _fmt

    def __init__(self, fmt, arg=None, **options):
        """
        ``arg`` must be an iterable of tuples (unicode_key, data_tuple).
        Data tuples will be converted to bytes with
        ``struct.pack(fmt, *data_tuple)``.

        Take a look at
        http://docs.python.org/library/struct.html#format-strings for the
        format string specification.
        """
        self._fmt = fmt
        self._struct = struct.Struct(str(fmt))
        super(RecordTrie, self).__init__(arg, **options)

    cdef _unpack(self, bytes value):
        return self._struct.unpack(value)

    cdef bytes _pack(self, value):
        return self._struct.pack(*value)

    def __reduce__(self):  # pickling support
        return self.__class__, (self._fmt,), self.tobytes()
