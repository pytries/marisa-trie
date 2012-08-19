from __future__ import unicode_literals

from std_iostream cimport stringstream, istream, ostream
cimport keyset
cimport key
cimport query
cimport agent
cimport trie
cimport iostream


cdef class Trie:
    """
    MARISA-trie is a succint Trie data structure. It stores unicode keys
    in a memory-efficient structure and auto-assigns unique ID to each key
    (which can be then used to associate a value with a key).

    Supported operations are key lookups (get ID or error given a key),
    reverse key lookups (get a key given its ID) and prefix lookups
    (get all prefixes of a given key from this trie).
    """

    cdef trie.Trie* _trie

    def __cinit__(self):
        self._trie = new trie.Trie()
        self.build([]) # create an empty trie

    def __dealloc__(self):
        if self._trie:
            del self._trie

    def __contains__(self, unicode key):
        cdef bytes _key = key.encode('utf8')
        return self._contains(_key)

    def __len__(self):
        return self._trie.num_keys()

    cpdef int key_id(self, unicode key) except -1:
        """
        Returns unique auto-generated key index for a ``key``.
        Raises KeyError if key is not in this trie.
        """
        cdef bytes _key = key.encode('utf8')
        cdef int res = self._key_id(_key)
        if res == -1:
            raise KeyError(key)
        return res

    cpdef unicode restore_key(self, int index):
        """
        Returns a key given its index (obtained by ``key_id`` method).
        """
        cdef agent.Agent ag
        ag.set_query(index)
        try:
            self._trie.reverse_lookup(ag)
        except KeyError:
            raise KeyError(index)
        cdef bytes _key = ag.key().ptr()
        return _key.decode('utf8')

    cdef int _key_id(self, char* key):
        cdef bint res
        cdef agent.Agent ag
        ag.set_query(key)
        res = self._trie.lookup(ag)
        if not res:
            return -1
        return ag.key().id()

    cdef bint _contains(self, char* key):
        cdef agent.Agent ag
        ag.set_query(key)
        return self._trie.lookup(ag)

    def read(self, f):
        """
        Reads a trie from an open file object.

        Works only with "real" disk-based file objects,
        file-like objects are not supported.
        """
        self._trie.read(f.fileno())

    def write(self, f):
        """
        Reads a trie to an open file object.

        Works only with "real" disk-based file objects,
        file-like objects are not supported.
        """
        self._trie.write(f.fileno())

    def save(self, path):
        """
        Saves trie to a file.
        """
        with open(path, 'w') as f:
            self.write(f)

    def load(self, path):
        """
        Loads trie from a file.
        """
        with open(path, 'r') as f:
            self.read(f)

    cpdef bytes dumps(self) except +:
        """
        Returns raw trie content as bytes.
        """
        cdef stringstream stream
        iostream.write((<ostream *> &stream)[0], self._trie[0])
        cdef bytes res = stream.str()
        return res

    cpdef loads(self, bytes data) except +:
        """
        Loads trie from bytes ``data``.
        """
        cdef stringstream* stream = new stringstream(data)
        try:
            iostream.read((<istream *> stream)[0], self._trie)
        finally:
            del stream


    def __reduce__(self): # pickling support
        return self.__class__, tuple(), self.dumps()

    def __setstate__(self, state): # pickling support
        self.loads(state)


    def mmap(self, path):
        """
        Mmaps trie to a file; this allows lookups without loading full
        trie to memory.
        """
        import sys
        str_path = path.encode(sys.getfilesystemencoding())
        cdef char* c_path = str_path
        self._trie.mmap(c_path)

    def build(self, unicode_keys, int config_flags=0):
        """
        Builds the trie using values from ``unicode_keys`` iterable.
        """
        byte_keys = (key.encode('utf8') for key in sorted(unicode_keys))
        cdef char* c_str

        cdef keyset.Keyset *ks = new keyset.Keyset()

        try:
            for key in byte_keys:
                c_str = key
                ks.push_back(c_str)

            self._trie.build(ks[0], config_flags)
            return self
        finally:
            del ks

    def iter_prefixes(self, unicode key):
        """
        Returns an iterator of all prefixes of a given key.
        """
        cdef agent.Agent ag
        cdef bytes b_prefix

        cdef bytes b_key = key.encode('utf8')
        ag.set_query(b_key)

        while self._trie.common_prefix_search(ag):
            b_prefix = ag.key().ptr()[:ag.key().length()]
            yield b_prefix.decode('utf8')

    def prefixes(self, unicode key):
        """
        Returns a list with all prefixes of a given key.
        """

        # this an inlined version of ``list(self.iter_prefixes(key))``

        cdef agent.Agent ag
        cdef bytes b_prefix
        cdef list res = []

        cdef bytes b_key = key.encode('utf8')
        ag.set_query(b_key)

        while self._trie.common_prefix_search(ag):
            b_prefix = ag.key().ptr()[:ag.key().length()]
            res.append(b_prefix.decode('utf8'))
        return res

    def iterkeys(self, unicode prefix=""):
        """
        Returns an iterator over keys that have a prefix ``prefix``.
        """
        cdef agent.Agent ag
        cdef bytes b_key

        cdef bytes b_prefix = prefix.encode('utf8')
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            b_key = ag.key().ptr()[:ag.key().length()]
            yield b_key.decode('utf8')

    def keys(self, unicode prefix=""):
        """
        Returns a list with all keys with a prefix ``prefix``.
        """

        # this an inlined version of ``list(self.iterkeys(prefix))``

        cdef list res = []
        cdef agent.Agent ag
        cdef bytes b_key

        cdef bytes b_prefix = prefix.encode('utf8')
        ag.set_query(b_prefix)

        while self._trie.predictive_search(ag):
            b_key = ag.key().ptr()[:ag.key().length()]
            res.append(b_key.decode('utf8'))

        return res

